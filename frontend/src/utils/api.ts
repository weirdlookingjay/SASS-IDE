import axios from 'axios';
import { Workspace, GitTemplate, ResourceClass } from '@/types/workspace';

interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

interface LoginResponse {
  username: string;
  email: string;
  access: string;
  refresh: string;
}

interface ApiResponse<T> {
  data: T;
  message?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL
});

// Add request interceptor to handle auth
api.interceptors.request.use(
  (config) => {
    // Always set Content-Type for JSON
    if (config.headers) {
      config.headers['Content-Type'] = 'application/json';
    }

    // Add auth token if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle 401s and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Try token refresh if 401 and haven't tried yet
    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      originalRequest?.url !== '/api/jwt/login/' && // Don't refresh on login failures
      originalRequest?.url !== '/api/jwt/token/refresh/' && // Don't refresh on refresh failures
      localStorage.getItem('refresh_token')
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/api/jwt/token/refresh/`, {
          refresh: refreshToken
        });

        if (response.data.access) {
          localStorage.setItem('access_token', response.data.access);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          }
          return api(originalRequest);
        }
      } catch (error: unknown) {
        const axiosError = error as { response?: { status: number } };
        console.error('Token refresh failed:', error);
        // Only clear tokens if refresh token is invalid/expired
        if (axiosError.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          // If we're not on the login page, redirect to it
          if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error); // Return original error
      }
    }

    // Don't clear tokens here - we only clear them if refresh token is invalid

    return Promise.reject(error);
  }
);

export const auth = {
  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    try {
      console.log('Attempting login with:', { username, API_URL });
      
      const response = await api.post('/api/jwt/login/', { 
        username, 
        password 
      });
      
      console.log('Login response:', response);
      
      const { access, refresh, username: responseUsername, email } = response.data;
      
      // Return tokens to be stored by AuthProvider
      
      return { 
        data: { 
          username: responseUsername,
          email,
          access,
          refresh
        } 
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async me(): Promise<ApiResponse<User>> {
    const token = localStorage.getItem('access_token');
    const response = await api.get('/api/jwt/me/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return { data: response.data };
  },

  async logout() {
    try {
      await api.post('/api/users/logout/', {}, { 
        headers: {
          'Content-Type': 'application/json',
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete api.defaults.headers.common['Authorization'];
    }
  },


  register: (data: { username: string; email: string; password: string }) => 
    api.post('/api/users/register/', data),
};

export const workspaces = {
  list: async (): Promise<ApiResponse<Workspace[]>> => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token available');
      }
      
      const response = await api.get('/api/workspaces/');
      return { data: response.data };
    } catch (error) {
      console.error('Failed to fetch workspaces:', error);
      throw error;
    }
  },

  create: async (data: Partial<Workspace>): Promise<ApiResponse<Workspace>> => {
    const response = await api.post('/api/workspaces/', data);
    return response;
  },

  get: async (id: string): Promise<ApiResponse<Workspace>> => {
    const response = await api.get(`/api/workspaces/${id}/`);
    return response;
  },

  delete: async (id: string): Promise<ApiResponse<void>> => {
    await api.delete(`/api/workspaces/${id}/`);
    return { data: undefined };
  },

  start: async (id: string): Promise<ApiResponse<void>> => {
    await api.post(`/api/workspaces/${id}/start/`);
    return { data: undefined };
  },

  stop: async (id: string): Promise<ApiResponse<void>> => {
    await api.post(`/api/workspaces/${id}/stop/`);
    return { data: undefined };
  },

  templates: () => 
    api.get<GitTemplate[]>('/api/workspaces/templates/').then(response => response.data),

  resources: () => 
    api.get<ResourceClass[]>('/api/workspaces/resources/').then(response => response.data),

  logs: (id: string) => 
    api.get<string[]>(`/api/workspaces/${id}/logs/`).then(response => response.data),
};

export default api;
