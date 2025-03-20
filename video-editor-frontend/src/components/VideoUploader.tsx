import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

interface VideoUploaderProps {
  onVideoSelect: (file: File) => void;
}

export const VideoUploader: React.FC<VideoUploaderProps> = ({ onVideoSelect }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      onVideoSelect(file);
    }
  }, [onVideoSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv']
    },
    maxFiles: 1,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto p-6"
    >
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200 ease-in-out
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
        `}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="flex justify-center">
            <svg
              className={`w-16 h-16 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div className="text-lg font-medium text-gray-900">
            {isDragActive ? 'Drop your video here' : 'Drag & drop your video here'}
          </div>
          <div className="text-sm text-gray-500">
            or click to select a file
          </div>
          <div className="text-xs text-gray-400">
            Supported formats: MP4, MOV, AVI, MKV
          </div>
        </div>
      </div>
    </motion.div>
  );
}; 