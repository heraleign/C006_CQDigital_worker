import axios, { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import type { ApiResponse } from '@/types';
import { mockHandler } from './mock';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Check if mock mode is enabled
const useMock = import.meta.env.VITE_USE_MOCK === 'true';

// Response interceptor - unwrap ApiResponse
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // If mock mode is on, the mock handler already returned unwrapped data
    return response.data;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      switch (status) {
        case 401:
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          console.error('权限不足');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 500:
          console.error('服务器错误');
          break;
        default:
          console.error(data?.message || '请求失败');
      }
    } else if (error.request) {
      console.error('网络错误，请检查网络连接');
    }
    return Promise.reject(error);
  }
);

// ===== Mock integration =====
// When VITE_USE_MOCK=true, the mockHandler intercepts all requests
// by wrapping the request method
if (useMock) {
  const originalRequest = api.request;
  api.request = async function mockRequest(config: any): Promise<any> {
    const method = (config.method || 'get').toLowerCase();
    const url = config.url || '';
    const params = method === 'get' ? config.params : config.data;

    const result = mockHandler(method, url, params);
    if (result !== null) {
      return Promise.resolve({
        code: 0,
        message: 'success',
        data: result,
      });
    }
    return originalRequest.call(api, config);
  } as typeof api.request;

  // Also wrap individual HTTP method shortcuts
  const methods = ['get', 'post', 'put', 'delete'] as const;
  methods.forEach((method) => {
    const originalMethod = (api as any)[method].bind(api);
    (api as any)[method] = function mockMethod(url: string, dataOrConfig?: any, config?: any) {
      const params = method === 'get' ? dataOrConfig : dataOrConfig;
      const result = mockHandler(method, url, params);
      if (result !== null) {
        return Promise.resolve({
          code: 0,
          message: 'success',
          data: result,
        });
      }
      return originalMethod(url, dataOrConfig, config);
    };
  });
}

export default api;
