import axios from 'axios';

// Connect to the API Gateway at port 8000
const api = axios.create({
  baseURL: window._env_?.VITE_API_HOST || import.meta.env.VITE_API_HOST || 'http://localhost:8000' || 'https://api.puneetdevops.online',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
