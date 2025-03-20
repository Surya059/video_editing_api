import axios from 'axios';

// Use relative URLs that will be handled by the Vite proxy
const API_BASE_URL = '';

export const videoService = {
  async trimVideo(file: File, startTime: number, endTime: number): Promise<Blob> {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('startTime', startTime.toString());
    formData.append('endTime', endTime.toString());

    const response = await axios.post(`${API_BASE_URL}/api/trim-video`, formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
}; 