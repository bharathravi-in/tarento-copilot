import axios from 'axios';
import type {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse,
} from 'axios';
import { config, TOKEN_KEY } from '../config';
import { logger } from '../utils/logger';
import { parseApiError, getErrorMessage } from '../utils/errorHandler';

/**
 * Create and configure axios instance with interceptors
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: config.api.baseURL,
    timeout: config.api.timeout,
  });

  // Request interceptor: Add auth token and handle content type
  client.interceptors.request.use(
    (cfg: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        cfg.headers.Authorization = `Bearer ${token}`;
      }
      
      // Don't override content-type for FormData (multipart/form-data)
      // Axios will set it automatically with the boundary
      if (!(cfg.data instanceof FormData)) {
        cfg.headers['Content-Type'] = 'application/json';
      }
      
      logger.debug(`[${cfg.method?.toUpperCase()}] ${cfg.url}`);
      return cfg;
    },
    (error: AxiosError) => {
      logger.error('Request error', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor: Handle errors and token refresh
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      logger.debug(`[${response.status}] ${response.config.url}`);
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
      };

      // Handle 401 - Unauthorized
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        logger.warn('Token expired, attempting refresh...');
        
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const response = await axios.post(
              `${config.api.baseURL}/auth/refresh`,
              { refresh_token: refreshToken }
            );
            
            const { access_token } = response.data;
            localStorage.setItem(TOKEN_KEY, access_token);
            
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            
            return client(originalRequest);
          } else {
            // No refresh token, redirect to login
            localStorage.removeItem(TOKEN_KEY);
            window.location.href = '/login';
          }
        } catch (refreshError) {
          logger.error('Token refresh failed', refreshError);
          localStorage.removeItem(TOKEN_KEY);
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      // Log error details
      const errorMsg = getErrorMessage(error);
      logger.error(`API Error: ${errorMsg}`, {
        status: error.response?.status,
        url: error.config?.url,
      });

      // Parse and throw error
      try {
        parseApiError(error);
      } catch (parsedError) {
        return Promise.reject(parsedError);
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();

/**
 * Check if request is successful
 */
export function isSuccessResponse(status: number): boolean {
  return status >= 200 && status < 300;
}
