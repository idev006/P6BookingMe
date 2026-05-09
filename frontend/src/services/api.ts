import axios from 'axios';

const apiBase = import.meta.env.VITE_API_URL || '/api/v1';
console.log('Axios BaseURL initialized as:', apiBase);

const api = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
