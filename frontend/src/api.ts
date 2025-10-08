import axios from 'axios';
import { ChatRequest, ChatResponse, RateLimitInfo, UserSubjectsResponse } from './types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      // Handle rate limiting
      throw {
        type: 'RATE_LIMIT',
        data: error.response.data,
      };
    }
    
    if (error.response?.status >= 500) {
      throw {
        type: 'SERVER_ERROR',
        message: 'Server error occurred. Please try again later.',
        data: error.response.data,
      };
    }
    
    throw {
      type: 'API_ERROR',
      message: error.response?.data?.error || error.message,
      data: error.response?.data,
    };
  }
);

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', request);
    return response.data;
  },

  clearSession: async (subject: string, email: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/clear-session', { subject, email });
    return response.data;
  },

  getRateLimitInfo: async (email: string): Promise<RateLimitInfo> => {
    const response = await api.get(`/rate-limit-info?email=${encodeURIComponent(email)}`);
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  getAnalytics: async (): Promise<any> => {
    const response = await api.get('/graphs');
    return response.data;
  },

  // Subject management
  getUserSubjects: async (email: string): Promise<UserSubjectsResponse> => {
    const response = await api.get(`/user/subjects?email=${encodeURIComponent(email)}`);
    return response.data;
  },

  addSubjectToUser: async (email: string, subjectId: string): Promise<UserSubjectsResponse> => {
    const response = await api.post('/user/subjects', { email, subject_id: subjectId });
    return response.data;
  },

  removeSubjectFromUser: async (email: string, subjectId: string): Promise<UserSubjectsResponse> => {
    const response = await api.delete(`/user/subjects/${subjectId}?email=${encodeURIComponent(email)}`);
    return response.data;
  },
};

export default api;
