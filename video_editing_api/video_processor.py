import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from video_editing_api.config import VIDEO_SETTINGS

class BaseOperation(ABC):
    """Base class for all video operations."""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
    
    @classmethod
    def get_video_info(cls, video_path: str) -> dict:
        """Get video information without creating an operation instance."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            return {
                "duration": duration,
                "fps": fps,
                "width": frame_width,
                "height": frame_height,
                "total_frames": total_frames
            }
        finally:
            cap.release()
    
    @abstractmethod
    def process(self) -> str:
        """Process the video and return the path to the processed video."""
        pass
    
    def _get_output_path(self, operation_name: str) -> str:
        """Generate a unique output path for the processed video."""
        return f"/tmp/{operation_name}_{os.urandom(4).hex()}.mp4"
    
    def _create_video_writer(self, output_path: str) -> cv2.VideoWriter:
        """Create a video writer with the specified output path."""
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_SETTINGS["codec"])
        return cv2.VideoWriter(
            output_path,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
    
    def _frame_to_time(self, frame_number: int) -> float:
        """Convert frame number to time in seconds."""
        return frame_number / self.fps
    
    def _time_to_frame(self, time: float) -> int:
        """Convert time in seconds to frame number."""
        return int(time * self.fps)
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'cap'):
            self.cap.release()

class CutOperation(BaseOperation):
    """Operation for cutting/trimming a video."""
    
    def __init__(self, video_path: str, start_time: float, end_time: float):
        super().__init__(video_path)
        
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
            
        self.start_time = start_time
        self.end_time = end_time
        
        # Convert times to frame numbers
        self.start_frame = self._time_to_frame(start_time)
        self.end_frame = self._time_to_frame(end_time)
        
        # Validate frame numbers
        if self.start_frame >= self.total_frames:
            raise ValueError("Start time is beyond video duration")
        if self.end_frame > self.total_frames:
            raise ValueError("End time is beyond video duration")
    
    def process(self) -> str:
        """Cut the video between start_time and end_time."""
        try:
            # Set the starting frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            
            # Create output video writer
            output_path = self._get_output_path("cut")
            out = self._create_video_writer(output_path)
            
            # Process frames
            frame_count = self.start_frame
            while frame_count < self.end_frame:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                out.write(frame)
                frame_count += 1
            
            # Clean up
            out.release()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")

class OperationFactory:
    """Factory class for creating video operations."""
    
    @staticmethod
    def create_operation(operation_type: str, video_path: str, **kwargs) -> BaseOperation:
        """Create a video operation instance based on the operation type."""
        operations = {
            "cut": CutOperation,
            # Add more operations here as they are implemented
        }
        
        if operation_type not in operations:
            raise ValueError(f"Unsupported operation type: {operation_type}")
        
        return operations[operation_type](video_path, **kwargs) 