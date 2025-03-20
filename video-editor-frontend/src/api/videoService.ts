import axios from 'axios';

// Use relative URLs that will be handled by the Vite proxy
const API_BASE_URL = '';

export const videoService = {
  async trimVideo(file: File, startTime: number, endTime: number): Promise<Blob> {
    console.log('Trimming video with params:', { fileName: file.name, startTime, endTime });
    
    if (startTime >= endTime) {
      throw new Error('Start time must be less than end time');
    }

    if (startTime < 0) {
      throw new Error('Start time must be non-negative');
    }

    const formData = new FormData();
    formData.append('video', file);
    formData.append('startTime', startTime.toString());
    formData.append('endTime', endTime.toString());

    // Log the request details
    console.log('Sending trim video request with:', {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size,
      startTime,
      endTime,
      formDataEntries: Array.from(formData.entries()).map(([key, value]) => ({
        key,
        value: value instanceof File ? `File: ${value.name}` : value
      }))
    });

    try {
      const response = await axios.post(`${API_BASE_URL}/api/trim-video`, formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Get the filename from the Content-Disposition header if available
      const contentDisposition = response.headers['content-disposition'];
      const filenameMatch = contentDisposition?.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      const filename = filenameMatch ? filenameMatch[1].replace(/['"]/g, '') : `trimmed_${file.name}`;

      // Create a new Blob with the correct type
      const blob = new Blob([response.data], { type: 'video/mp4' });
      
      // Create a download URL and trigger download
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      return blob;
    } catch (error: any) {
      console.error('Error trimming video:', error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response.data instanceof Blob) {
          const text = await error.response.data.text();
          try {
            const errorData = JSON.parse(text);
            throw new Error(errorData.detail || 'Failed to process video');
          } catch (e) {
            throw new Error('Failed to process video');
          }
        }
      }
      throw error;
    }
  },
}; 