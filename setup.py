from setuptools import setup, find_packages

setup(
    name="video-editing-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "pydantic==2.4.2",
        "python-jose==3.3.0",
        "python-dotenv==1.0.0",
        "opencv-python==4.8.1.78",
        "numpy==1.26.2",
        "boto3==1.34.34",
        "sqlalchemy==2.0.27",
        "python-magic==0.4.27",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.1",
            "pytest-cov==4.1.0",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A RESTful API for video editing operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/video-editing-api",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 