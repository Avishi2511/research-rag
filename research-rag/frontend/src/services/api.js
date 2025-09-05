import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const uploadPDFs = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Upload failed');
  }
};

export const askQuestion = async (questionData) => {
  try {
    const response = await api.post('/ask', questionData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get answer');
  }
};

export const getDocuments = async () => {
  try {
    const response = await api.get('/documents');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get documents');
  }
};

export const getStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get stats');
  }
};

export const clearAllData = async () => {
  try {
    const response = await api.delete('/clear');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to clear data');
  }
};

export default api;
