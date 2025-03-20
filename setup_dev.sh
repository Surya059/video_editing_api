#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install the package in development mode with test dependencies
pip install -e ".[dev]"

# Create necessary directories
mkdir -p video_editing_api/uploads
mkdir -p video_editing_api/processed

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To run tests: pytest"
echo "To start the API: uvicorn video_editing_api.main:app --reload" 