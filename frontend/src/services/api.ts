import axios from 'axios';

// Base API URL - Update this with your actual backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Set to true if backend uses cookies
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
      return Promise.reject({
        message: 'Network error. Please check your connection and try again.',
        originalError: error
      });
    }

    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem('refresh_token', response.data.refresh_token);
          // Retry the original request
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(error.config);
        } catch (refreshError) {
          // Refresh failed, logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
      }
    }

    // Log error for debugging
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
    });

    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    college?: string;
    branch?: string;
    graduation_year?: number;
    target_role?: string;
  }) => api.post('/api/v1/auth/register', data),

  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }),

  logout: (refreshToken: string) =>
    api.post('/api/v1/auth/logout', { refresh_token: refreshToken }),

  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),

  getMe: () => api.get('/api/v1/auth/me'),
};

// User APIs
export const userAPI = {
  getProfile: () => api.get('/api/v1/users/me'),
  updateProfile: (data: any) => api.put('/api/v1/users/me', data),
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getPreferences: () => api.get('/api/v1/users/me/preferences'),
  updatePreferences: (data: any) => api.put('/api/v1/users/me/preferences', data),
  getIntegrations: () => api.get('/api/v1/users/me/integrations'),
  connectPlatforms: (data: any) => api.post('/api/v1/users/me/integrations', data),
  deleteAccount: () => api.delete('/api/v1/users/me'),
};

// Resume APIs
export const resumeAPI = {
  upload: (file: File, isPrimary = false, analyze = true, targetRole?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/resumes/upload', formData, {
      params: { is_primary: isPrimary, analyze, target_role: targetRole },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/api/v1/resumes/list'),
  get: (resumeId: string) => api.get(`/api/v1/resumes/${resumeId}`),
  delete: (resumeId: string) => api.delete(`/api/v1/resumes/${resumeId}`),
  analyze: (resumeId: string, targetRole?: string) =>
    api.post(`/api/v1/resumes/${resumeId}/analyze`, null, {
      params: { target_role: targetRole },
    }),
  getAnalysis: (resumeId: string) => api.get(`/api/v1/resumes/${resumeId}/analysis`),
  setPrimary: (resumeId: string) => api.post(`/api/v1/resumes/${resumeId}/set-primary`),
  download: (resumeId: string) => api.get(`/api/v1/resumes/${resumeId}/download`),
  compareWithJob: (resumeId: string, jobDescription: string, jobTitle: string) =>
    api.post(`/api/v1/resumes/${resumeId}/compare`, { job_description: jobDescription, job_title: jobTitle }),
};

// Interview APIs
export const interviewAPI = {
  create: (data: {
    interview_type: string;
    target_role: string;
    technologies: string[];
    difficulty: string;
    num_questions: number;
  }) => api.post('/api/v1/interviews/create', data),
  list: (status?: string) => api.get('/api/v1/interviews/list', { params: { status } }),
  get: (interviewId: string) => api.get(`/api/v1/interviews/${interviewId}`),
  delete: (interviewId: string) => api.delete(`/api/v1/interviews/${interviewId}`),
  regenerateQuestions: (interviewId: string) =>
    api.post(`/api/v1/interviews/${interviewId}/regenerate-questions`),
  getResult: (interviewId: string) => api.get(`/api/v1/interviews/${interviewId}/result`),
  getTranscript: (interviewId: string) => api.get(`/api/v1/interviews/${interviewId}/transcript`),
  getStats: () => api.get('/api/v1/interviews/stats/summary'),
};

export default api;

