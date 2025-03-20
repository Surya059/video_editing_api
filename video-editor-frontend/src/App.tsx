import React, { useState, useRef } from 'react';
import { VideoUploader } from './components/VideoUploader';
import { VideoPlayer } from './components/VideoPlayer';
import { VideoControls } from './components/VideoControls';
import { videoService } from './api/videoService';

export const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleVideoSelect = (file: File) => {
    setSelectedFile(file);
    setCurrentTime(0);
    setStartTime(0);
    
    // Create a temporary video element to get the duration
    const video = document.createElement('video');
    video.src = URL.createObjectURL(file);
    video.onloadedmetadata = () => {
      setEndTime(video.duration);
      setDuration(video.duration);
      URL.revokeObjectURL(video.src);
    };
  };

  const handleExport = async () => {
    if (!selectedFile) return;

    try {
      const blob = await videoService.trimVideo(selectedFile, startTime, endTime);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trimmed_${selectedFile.name}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error processing video:', error);
      alert('Failed to process video. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Video Editor</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {!selectedFile ? (
            <VideoUploader onVideoSelect={handleVideoSelect} />
          ) : (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-lg font-medium text-gray-900">Selected Video</h2>
                      <p className="text-sm text-gray-500">{selectedFile.name}</p>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-sm text-blue-500 hover:text-blue-600"
                    >
                      Choose different video
                    </button>
                  </div>

                  <VideoPlayer
                    file={selectedFile}
                    currentTime={currentTime}
                    onTimeUpdate={setCurrentTime}
                  />
                </div>
              </div>

              <VideoControls
                duration={duration}
                currentTime={currentTime}
                startTime={startTime}
                endTime={endTime}
                onTimeChange={setCurrentTime}
                onStartTimeChange={setStartTime}
                onEndTimeChange={setEndTime}
              />

              <div className="flex justify-end">
                <button
                  onClick={handleExport}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Export Trimmed Video
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}; 