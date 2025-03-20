import os
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from video_editing_api.main import app
from video_editing_api.config import UPLOAD_DIR, PROCESSED_DIR

client = TestClient(app)

@pytest.fixture
def test_video():
    """Create a test video file."""
    test_video_path = os.path.join(UPLOAD_DIR, "test_video.mp4")
    
    # Create a test video using OpenCV
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video_path, fourcc, fps, (width, height))
    
    # Generate frames
    for _ in range(fps * duration):
        # Create a colored frame with some text
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (0, 0, 255)  # Red background
        cv2.putText(frame, 'Test Video', (width//4, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    return test_video_path

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test files after each test."""
    yield
    for file in os.listdir(UPLOAD_DIR):
        try:
            os.remove(os.path.join(UPLOAD_DIR, file))
        except:
            pass
    for file in os.listdir(PROCESSED_DIR):
        try:
            os.remove(os.path.join(PROCESSED_DIR, file))
        except:
            pass

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Video Editing API"

def test_upload_video(test_video):
    """Test video upload endpoint."""
    with open(test_video, "rb") as f:
        response = client.post(
            "/api/v1/videos/upload",
            files={"file": ("test_video.mp4", f, "video/mp4")}
        )
    assert response.status_code == 200
    assert "video_id" in response.json()
    return response.json()["video_id"]

def test_cut_video(test_video):
    """Test video cutting endpoint."""
    # First upload a video
    video_id = test_upload_video(test_video)
    
    # Test cutting the video
    response = client.post(
        f"/api/v1/videos/{video_id}/cut",
        json={
            "start_time": 0.0,
            "end_time": 5.0,
            "output_format": "mp4"
        }
    )
    assert response.status_code == 200
    assert "processed_video_id" in response.json()
    return response.json()["processed_video_id"]

def test_get_video(test_video):
    """Test getting a processed video."""
    # First upload and process a video
    processed_id = test_cut_video(test_video)
    
    # Test getting the processed video
    response = client.get(f"/api/v1/videos/{processed_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"

def test_invalid_video_id():
    """Test getting a non-existent video."""
    response = client.get("/api/v1/videos/nonexistent")
    assert response.status_code == 404

def test_invalid_cut_parameters(test_video):
    """Test cutting with invalid parameters."""
    video_id = test_upload_video(test_video)
    
    # Test with end time before start time
    response = client.post(
        f"/api/v1/videos/{video_id}/cut",
        json={
            "start_time": 5.0,
            "end_time": 2.0,
            "output_format": "mp4"
        }
    )
    assert response.status_code == 500 