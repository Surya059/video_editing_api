from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create database directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Create SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///data/video_editing.db"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    filename = Column(String)
    s3_key = Column(String)
    content_type = Column(String)
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    total_frames = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processed_videos = relationship("ProcessedVideo", back_populates="original_video")

class ProcessedVideo(Base):
    __tablename__ = "processed_videos"

    id = Column(Integer, primary_key=True, index=True)
    processed_video_id = Column(String, unique=True, index=True)
    original_video_id = Column(String, ForeignKey("videos.video_id"))
    filename = Column(String)
    s3_key = Column(String)
    content_type = Column(String)
    operation_type = Column(String)
    operation_params = Column(JSON)
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    total_frames = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    original_video = relationship("Video", back_populates="processed_videos")

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 