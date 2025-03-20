import cv2
import numpy as np

# Create a video writer
cap = cv2.VideoWriter('test_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))

# Generate 10 seconds of video (30 fps * 10 seconds = 300 frames)
for _ in range(300):
    # Create a red frame
    frame = np.full((480, 640, 3), (0, 0, 255), dtype=np.uint8)
    # Add text
    cv2.putText(frame, 'Test Video', (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Write the frame
    cap.write(frame)

# Release the video writer
cap.release() 