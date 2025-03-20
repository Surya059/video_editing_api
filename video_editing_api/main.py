import os
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from video_editing_api.config import MAX_FILE_SIZE, ALLOWED_VIDEO_FORMATS
from video_editing_api.video_processor import OperationFactory, BaseOperation
from video_editing_api.database import get_db, Video, ProcessedVideo
from video_editing_api.s3_service import S3Service

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Editing API",
    description="API for video editing operations",
    version="1.0.0"
)

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # Allow frontend to see the filename
)

# Initialize S3 service
s3_service = S3Service("my-app-unique-bucket-1742462086")

class CutOperationParams(BaseModel):
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., gt=0, description="End time in seconds")
    output_format: Optional[str] = "mp4"

@app.post("/api/v1/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a video file to S3 and store metadata in SQLite.
    Returns a video ID that can be used for subsequent operations.
    """
    # Log the content type for debugging
    print(f"Received file with content type: {file.content_type}")
    
    # Validate file size
    file_size = 0
    file.file.seek(0, 2)  # Seek to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Get file extension and determine content type
    file_extension = os.path.splitext(file.filename)[1].lower()
    content_type = file.content_type
    
    # Map file extensions to content types
    extension_to_content_type = {
        '.mov': 'video/quicktime',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska'
    }
    
    # If content type is application/octet-stream, try to determine it from extension
    if content_type == 'application/octet-stream' and file_extension in extension_to_content_type:
        content_type = extension_to_content_type[file_extension]
    
    # Validate content type
    if content_type not in ALLOWED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported video format: {content_type}. Allowed formats: {ALLOWED_VIDEO_FORMATS}"
        )
    
    # Generate unique filename and S3 key
    video_id = str(uuid.uuid4())
    filename = f"{video_id}{file_extension}"
    s3_key = f"videos/{filename}"
    
    # Upload to S3
    if not s3_service.upload_file(file.file, s3_key, content_type):
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")
    
    # Get video information
    try:
        # Download the file temporarily to get video info
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "wb") as f:
            f.write(s3_service.download_file(s3_key))
        
        video_info = BaseOperation.get_video_info(temp_path)
        os.remove(temp_path)  # Clean up temporary file
        
        # Create database record
        db_video = Video(
            video_id=video_id,
            filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            duration=video_info["duration"],
            width=video_info["width"],
            height=video_info["height"],
            fps=video_info["fps"],
            total_frames=video_info["total_frames"]
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        
        return {"video_id": video_id, "message": "Video uploaded successfully"}
        
    except Exception as e:
        # Clean up S3 file if database operation fails
        s3_service.delete_file(s3_key)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/videos/{video_id}/cut")
async def cut_video(
    video_id: str,
    params: CutOperationParams,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cut a video segment between start_time and end_time.
    Returns a job ID for tracking the processing status.
    """
    # Get video from database
    db_video = db.query(Video).filter(Video.video_id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        # Validate times against video duration
        if params.start_time >= db_video.duration:
            raise HTTPException(
                status_code=400,
                detail=f"Start time ({params.start_time}s) must be less than video duration ({db_video.duration:.2f}s)"
            )
        if params.end_time > db_video.duration:
            raise HTTPException(
                status_code=400,
                detail=f"End time ({params.end_time}s) must be less than or equal to video duration ({db_video.duration:.2f}s)"
            )
        
        # Download video from S3
        temp_input_path = f"/tmp/{db_video.filename}"
        with open(temp_input_path, "wb") as f:
            f.write(s3_service.download_file(db_video.s3_key))
        
        # Create cut operation
        operation = OperationFactory.create_operation(
            "cut",
            temp_input_path,
            start_time=params.start_time,
            end_time=params.end_time
        )
        
        # Process video
        output_path = operation.process()
        
        # Upload processed video to S3
        processed_id = str(uuid.uuid4())
        processed_filename = f"{processed_id}.mp4"
        s3_key = f"processed/{processed_filename}"
        
        with open(output_path, "rb") as f:
            if not s3_service.upload_file(f, s3_key, "video/mp4"):
                raise HTTPException(status_code=500, detail="Failed to upload processed video to S3")
        
        # Get processed video information
        processed_info = BaseOperation.get_video_info(output_path)
        
        # Create database record for processed video
        db_processed = ProcessedVideo(
            processed_video_id=processed_id,
            original_video_id=video_id,
            filename=processed_filename,
            s3_key=s3_key,
            content_type="video/mp4",
            operation_type="cut",
            operation_params=params.dict(),
            duration=processed_info["duration"],
            width=processed_info["width"],
            height=processed_info["height"],
            fps=processed_info["fps"],
            total_frames=processed_info["total_frames"]
        )
        db.add(db_processed)
        db.commit()
        db.refresh(db_processed)
        
        # Clean up temporary files
        os.remove(temp_input_path)
        os.remove(output_path)
        
        return {
            "processed_video_id": processed_id,
            "message": "Video processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/videos/{video_id}")
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """
    Get a processed video file.
    """
    # Check both original and processed videos
    db_video = db.query(Video).filter(Video.video_id == video_id).first()
    db_processed = db.query(ProcessedVideo).filter(ProcessedVideo.processed_video_id == video_id).first()
    
    if not db_video and not db_processed:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Use processed video if available, otherwise use original
    video_data = db_processed if db_processed else db_video
    
    # Generate presigned URL
    url = s3_service.get_file_url(video_data.s3_key)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
    
    return RedirectResponse(url=url)

@app.get("/api/v1/videos/{video_id}/info")
async def get_video_info(video_id: str, db: Session = Depends(get_db)):
    """
    Get information about a video file.
    """
    # Check both original and processed videos
    db_video = db.query(Video).filter(Video.video_id == video_id).first()
    db_processed = db.query(ProcessedVideo).filter(ProcessedVideo.processed_video_id == video_id).first()
    
    if not db_video and not db_processed:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Use processed video if available, otherwise use original
    video_data = db_processed if db_processed else db_video
    
    return {
        "video_id": video_data.video_id if isinstance(video_data, Video) else video_data.processed_video_id,
        "filename": video_data.filename,
        "content_type": video_data.content_type,
        "duration": video_data.duration,
        "width": video_data.width,
        "height": video_data.height,
        "fps": video_data.fps,
        "total_frames": video_data.total_frames,
        "created_at": video_data.created_at,
        "updated_at": video_data.updated_at,
        "operation_type": getattr(video_data, "operation_type", None),
        "operation_params": getattr(video_data, "operation_params", None)
    }

@app.post("/api/trim-video")
async def trim_video(
    video: UploadFile = File(...),
    startTime: str = Form(...),
    endTime: str = Form(...)
):
    """
    Trim a video file directly without storing it in the database.
    Returns the trimmed video file.
    """
    temp_input_path = None
    temp_output_path = None
    
    try:
        logger.info(f"Received trim request - File: {video.filename}, Start: {startTime}, End: {endTime}")
        
        # Create temporary directory if it doesn't exist
        os.makedirs("/tmp", exist_ok=True)

        # Save uploaded file temporarily
        temp_input_path = f"/tmp/input_{uuid.uuid4().hex}_{video.filename}"
        logger.debug(f"Saving uploaded file to: {temp_input_path}")
        with open(temp_input_path, "wb") as f:
            content = await video.read()
            f.write(content)
        logger.debug(f"File saved, size: {os.path.getsize(temp_input_path)} bytes")

        # Get video duration first
        logger.debug("Getting video info...")
        video_info = BaseOperation.get_video_info(temp_input_path)
        logger.info(f"Video info: {video_info}")
        
        start_time = float(startTime)
        end_time = float(endTime)
        logger.debug(f"Parsed times - Start: {start_time}, End: {end_time}")

        # Validate times
        if start_time >= video_info["duration"]:
            msg = f"Start time ({start_time}s) must be less than video duration ({video_info['duration']:.2f}s)"
            logger.error(msg)
            raise HTTPException(status_code=400, detail=msg)
        if end_time > video_info["duration"]:
            msg = f"End time ({end_time}s) must be less than or equal to video duration ({video_info['duration']:.2f}s)"
            logger.error(msg)
            raise HTTPException(status_code=400, detail=msg)
        if start_time >= end_time:
            msg = f"Start time ({start_time}s) must be less than end time ({end_time}s)"
            logger.error(msg)
            raise HTTPException(status_code=400, detail=msg)

        # Create cut operation
        logger.debug("Creating cut operation...")
        operation = OperationFactory.create_operation(
            "cut",
            temp_input_path,
            start_time=start_time,
            end_time=end_time
        )

        # Process video
        logger.debug("Processing video...")
        temp_output_path = operation.process()
        logger.info(f"Video processed successfully, output at: {temp_output_path}")

        # Return the processed video file
        logger.debug("Returning processed video...")
        response = FileResponse(
            temp_output_path,
            media_type="video/mp4",
            filename=f"trimmed_{video.filename}",
            background=BackgroundTasks()
        )
        
        # Add cleanup of files as a background task
        response.background.add_task(cleanup_files, temp_input_path, temp_output_path)
        return response

    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        # Clean up
        cleanup_files(temp_input_path, temp_output_path)
        raise he
    except ValueError as ve:
        logger.error(f"Value Error: {str(ve)}")
        # Clean up
        cleanup_files(temp_input_path, temp_output_path)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Clean up
        cleanup_files(temp_input_path, temp_output_path)
        raise HTTPException(status_code=500, detail=str(e))

def cleanup_files(input_path, output_path):
    """Helper function to clean up temporary files"""
    if input_path and os.path.exists(input_path):
        os.remove(input_path)
    if output_path and os.path.exists(output_path):
        os.remove(output_path)

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Video Editing API",
        "version": "1.0.0",
        "documentation": "/docs"
    }
