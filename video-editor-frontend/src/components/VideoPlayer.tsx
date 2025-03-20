import React, { useRef, useEffect } from 'react';

interface VideoPlayerProps {
  file: File;
  currentTime: number;
  onTimeUpdate: (time: number) => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ file, currentTime, onTimeUpdate }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const videoUrl = useRef<string>('');

  useEffect(() => {
    if (file) {
      // Revoke the previous URL to avoid memory leaks
      if (videoUrl.current) {
        URL.revokeObjectURL(videoUrl.current);
      }
      videoUrl.current = URL.createObjectURL(file);
      if (videoRef.current) {
        videoRef.current.src = videoUrl.current;
      }
    }

    return () => {
      if (videoUrl.current) {
        URL.revokeObjectURL(videoUrl.current);
      }
    };
  }, [file]);

  useEffect(() => {
    if (videoRef.current && Math.abs(videoRef.current.currentTime - currentTime) > 0.001) {
      videoRef.current.currentTime = currentTime;
    }
  }, [currentTime]);

  return (
    <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        className="w-full h-full"
        controls
        onTimeUpdate={(e) => onTimeUpdate(e.currentTarget.currentTime)}
      />
    </div>
  );
}; 