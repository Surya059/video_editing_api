import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_trim_request():
    # URL of the backend
    url = 'http://ec2-54-193-126-176.us-west-1.compute.amazonaws.com:8000/api/trim-video'
    
    # Create a test video if it doesn't exist
    if not os.path.exists('test_video.mp4'):
        logger.info("Creating test video...")
        os.system('python3 create_test_video.py')
    
    # Log video file info
    video_size = os.path.getsize('test_video.mp4')
    logger.info(f"Test video size: {video_size} bytes")
    
    # Prepare the files and data
    files = {
        'video': ('test_video.mp4', open('test_video.mp4', 'rb'), 'video/mp4')
    }
    
    data = {
        'startTime': '0.1',
        'endTime': '0.3'
    }
    
    logger.info(f"Sending request with params: {data}")
    
    # Send the request
    try:
        response = requests.post(url, files=files, data=data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            # Save the trimmed video
            with open('trimmed_test_video.mp4', 'wb') as f:
                f.write(response.content)
            logger.info("Successfully saved trimmed video to trimmed_test_video.mp4")
        else:
            try:
                error_detail = response.json()
                logger.error(f"Error response: {error_detail}")
            except:
                logger.error(f"Error text: {response.text}")
                logger.error(f"Raw response content: {response.content}")
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
    finally:
        # Close the file
        files['video'][1].close()

if __name__ == '__main__':
    test_trim_request() 