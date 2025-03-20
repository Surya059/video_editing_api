import os

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Allowed video formats
ALLOWED_VIDEO_FORMATS = [
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska"
]

# Video processing settings
VIDEO_SETTINGS = {
    "output_format": "mp4",
    "codec": "mp4v",
    "quality": "high"
}

# Create data directory for SQLite database
os.makedirs("data", exist_ok=True) 