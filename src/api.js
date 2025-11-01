import axios from 'axios';

// Constants
export const API_VERSION = 'v1';
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Create axios instance with base configuration
const api = axios.create({
  baseURL: BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request queue for token refresh
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (callback) => {
  refreshSubscribers.push(callback);
};

const onTokenRefreshed = (token) => {
  refreshSubscribers.map(callback => callback(token));
  refreshSubscribers = [];
};

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('cadscribe_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add abort controller for each request
    const controller = new AbortController();
    config.signal = controller.signal;
    config.controller = controller; // Store for later use

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Note: Refresh endpoint not implemented in backend yet
        // For now, just logout on token expiry
        throw new Error('Token refresh not implemented');

      } catch (refreshError) {
        // If refresh fails, logout
        localStorage.removeItem('cadscribe_token');
        localStorage.removeItem('cadscribe_refresh_token');
        window.dispatchEvent(new Event('auth:logout'));
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);

      } finally {
        isRefreshing = false;
      }
    }

    // Retry failed requests
    if (error.response?.status >= 500 && !originalRequest._retryCount) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

      if (originalRequest._retryCount <= MAX_RETRIES) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * originalRequest._retryCount));
        return api(originalRequest);
      }
    }

    // Handle network errors and timeouts
    if (!error.response) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        console.warn('Request timeout:', error.config?.url);
        // Don't show offline notification for timeouts on non-critical endpoints
        if (!error.config?.url?.includes('/features') && !error.config?.url?.includes('/templates')) {
          window.dispatchEvent(new Event('api:offline'));
        }
      } else {
        // Show offline notification for other network errors
        window.dispatchEvent(new Event('api:offline'));
      }
    }

    return Promise.reject(error);
  }
);

// API modules with request caching and abort support
export const authAPI = {
  signup: (userData) => api.post('/signup', userData),
  login: async (credentials) => {
    const response = await api.post('/login', credentials);
    const { access_token } = response.data;
    localStorage.setItem('cadscribe_token', access_token);
    return response;
  },
  demoLogin: async () => {
    const response = await api.post('/demo');
    const { access_token } = response.data;
    localStorage.setItem('cadscribe_token', access_token);
    return response;
  },
  getCurrentUser: () => api.get('/me'),
  logout: () => {
    localStorage.removeItem('cadscribe_token');
    window.dispatchEvent(new Event('auth:logout'));
  },
};

// Request cache map
const requestCache = new Map();

const withCache = (key, request, ttl = 60000) => {
  const cached = requestCache.get(key);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.promise;
  }

  const promise = request();
  requestCache.set(key, { promise, timestamp: Date.now() });
  return promise;
};

// Projects API with caching
export const projectsAPI = {
  getAll: () => withCache('projects:all', () => api.get('/projects/')),
  getById: (id) => withCache(`projects:${id}`, () => api.get(`/projects/${id}`)),
  create: (projectData) => api.post('/projects/', projectData),
  update: (id, projectData) => {
    requestCache.delete(`projects:${id}`);
    requestCache.delete('projects:all');
    return api.put(`/projects/${id}`, projectData);
  },
  delete: (id) => {
    requestCache.delete(`projects:${id}`);
    requestCache.delete('projects:all');
    return api.delete(`/projects/${id}`);
  },
};

// Chat API with debouncing
let chatDebounceTimeout = null;
export const chatAPI = {
  getHistory: (projectId) => withCache(`chat:${projectId}`, () => api.get(`/ai/chat-history/${projectId}`)),
  sendMessage: (projectId, message) => {
    if (chatDebounceTimeout) {
      clearTimeout(chatDebounceTimeout);
    }

    return new Promise((resolve) => {
      chatDebounceTimeout = setTimeout(() => {
        resolve(api.post('/ai/chat', {
          project_id: projectId,
          message: message
        }));
      }, 300); // 300ms debounce
    });
  },
  generateCode: (description, engine = 'freecad') => api.post('/ai/generate-code', {
    description: description,
    engine: engine
  }),
};

// AI API with abort support
export const aiAPI = {
  getEngines: () => withCache('ai:engines', () => api.get('/ai/engines')),
  chat: (data, signal) => api.post('/ai/chat', data, { signal }),
  generateCode: (data, signal) => api.post('/ai/generate-code', data, { signal }),
};

// Models API with caching
export const modelsAPI = {
  generate: (data) => api.post('/models/generate', data),
  getAll: () => withCache('models:all', () => api.get('/models/')),
  getById: (id) => withCache(`models:${id}`, () => api.get(`/models/${id}`)),
  delete: (id) => {
    requestCache.delete(`models:${id}`);
    requestCache.delete('models:all');
    return api.delete(`/models/${id}`);
  },
};

// User API
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (profileData) => api.put('/user/profile', profileData),
  updateSettings: (settingsData) => api.put('/user/settings', settingsData),
  getSessions: () => api.get('/user/sessions'),
  changePassword: (passwordData) => api.post('/user/change-password', passwordData),
  deleteAccount: () => api.post('/user/delete'),
};

// CAD Service API
export const cadAPI = {
  generateModel: (data) => api.post('/models/generate', data),
  getSupportedFormats: () => withCache('cad:formats', () => api.get('/models/formats')),
  downloadFile: async (filePath, filename) => {
    try {
      const response = await api.get(`/files/${filePath}`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      console.error('Download error:', error);
      throw error;
    }
  }
};

// Misc API with shorter timeout for landing page
export const miscAPI = {
  getFeatures: () => withCache('misc:features', () => api.get('/features', { timeout: 10000 })),
  getTemplates: () => withCache('misc:templates', () => api.get('/templates', { timeout: 10000 })),
};

// Generic API functions for backward compatibility
export const getData = async (endpoint) => {
  try {
    const response = await api.get(endpoint);
    return response.data;
  } catch (error) {
    console.error("GET error:", error);
    throw error;
  }
};

export const postData = async (endpoint, payload) => {
  try {
    const response = await api.post(endpoint, payload);
    return response.data;
  } catch (error) {
    console.error("POST error:", error);
    throw error;
  }
};

export const putData = async (endpoint, payload) => {
  try {
    const response = await api.put(endpoint, payload);
    return response.data;
  } catch (error) {
    console.error("PUT error:", error);
    throw error;
  }
};

export const deleteData = async (endpoint) => {
  try {
    const response = await api.delete(endpoint);
    return response.data;
  } catch (error) {
    console.error("DELETE error:", error);
    throw error;
  }
};

export default api;
