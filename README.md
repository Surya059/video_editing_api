# Video Editing API

A RESTful API for video editing operations, built with FastAPI. This API provides endpoints for uploading videos and performing various video editing operations.

## Features

- Video upload
- Video cutting (trimming)
- Extensible architecture for adding more operations

## Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- Virtual environment (recommended)

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Video Upload
- `POST /api/v1/videos/upload`
  - Upload a video file
  - Returns a video ID for future operations

### Video Operations
- `POST /api/v1/videos/{video_id}/cut`
  - Cut a video segment
  - Parameters:
    - start_time: Start time in seconds
    - end_time: End time in seconds
    - output_format: Desired output format (mp4, mov, etc.)

## Adding New Operations

To add a new video operation:

1. Create a new operation class in `video_processor.py`:
   ```python
   class NewOperation(BaseOperation):
       def __init__(self, video_path: str, **kwargs):
           super().__init__(video_path)
           self.params = kwargs

       def process(self) -> str:
           # Implement your operation logic here
           pass
   ```

2. Add a new endpoint in `main.py`:
   ```python
   @router.post("/videos/{video_id}/new-operation")
   async def new_operation(
       video_id: str,
       params: NewOperationParams,
       background_tasks: BackgroundTasks
   ):
       # Implement endpoint logic
   ```

3. Update the documentation in this README

## Project Structure

```
.
├── main.py              # FastAPI application and endpoints
├── video_processor.py   # Video processing logic
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 