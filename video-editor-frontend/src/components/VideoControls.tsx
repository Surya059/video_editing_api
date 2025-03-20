import React from 'react';
import * as Slider from '@radix-ui/react-slider';

interface VideoControlsProps {
  duration: number;
  currentTime: number;
  startTime: number;
  endTime: number;
  onTimeChange: (time: number) => void;
  onStartTimeChange: (time: number) => void;
  onEndTimeChange: (time: number) => void;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  duration,
  currentTime,
  startTime,
  endTime,
  onTimeChange,
  onStartTimeChange,
  onEndTimeChange,
}) => {
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    const milliseconds = Math.floor((time % 1) * 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  };

  return (
    <div className="space-y-6 p-4 bg-white rounded-lg shadow">
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-700">Timeline</h3>
        <div className="relative pt-1">
          <Slider.Root
            className="relative flex items-center select-none touch-none w-full h-5"
            value={[currentTime]}
            max={duration}
            step={0.001}
            onValueChange={([value]) => onTimeChange(value)}
          >
            <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
              <Slider.Range className="absolute bg-blue-500 rounded-full h-full" />
            </Slider.Track>
            <Slider.Thumb
              className="block w-5 h-5 bg-white border-2 border-blue-500 rounded-full hover:bg-blue-50 focus:outline-none"
              aria-label="Time"
            />
          </Slider.Root>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-700">Trim Video</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-gray-500">Start Time</label>
            <Slider.Root
              className="relative flex items-center select-none touch-none w-full h-5"
              value={[startTime]}
              max={endTime}
              step={0.001}
              onValueChange={([value]) => onStartTimeChange(value)}
            >
              <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
                <Slider.Range className="absolute bg-green-500 rounded-full h-full" />
              </Slider.Track>
              <Slider.Thumb
                className="block w-5 h-5 bg-white border-2 border-green-500 rounded-full hover:bg-green-50 focus:outline-none"
                aria-label="Start time"
              />
            </Slider.Root>
            <div className="text-xs text-gray-500">{formatTime(startTime)}</div>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-gray-500">End Time</label>
            <Slider.Root
              className="relative flex items-center select-none touch-none w-full h-5"
              value={[endTime]}
              min={startTime}
              max={duration}
              step={0.001}
              onValueChange={([value]) => onEndTimeChange(value)}
            >
              <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
                <Slider.Range className="absolute bg-red-500 rounded-full h-full" />
              </Slider.Track>
              <Slider.Thumb
                className="block w-5 h-5 bg-white border-2 border-red-500 rounded-full hover:bg-red-50 focus:outline-none"
                aria-label="End time"
              />
            </Slider.Root>
            <div className="text-xs text-gray-500">{formatTime(endTime)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}; 