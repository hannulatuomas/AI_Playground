import axios, { AxiosInstance, AxiosError } from 'axios';

export class BaseService {
  protected static readonly REQUEST_TIMEOUT = 30000;
  protected static readonly MAX_RETRIES = 3;
  protected static readonly BACKOFF_MULTIPLIER = 2;
  protected static readonly INITIAL_BACKOFF = 1000;

  protected axiosInstance: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:3001') {
    this.axiosInstance = axios.create({
      baseURL,
      timeout: BaseService.REQUEST_TIMEOUT,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }
            const response = await this.axiosInstance.post('/auth/refresh', { refreshToken });
            const { token } = response.data;
            localStorage.setItem('token', token);
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return this.axiosInstance(originalRequest);
          } catch (refreshError) {
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            throw refreshError;
          }
        }
        throw error;
      }
    );
  }

  protected handleResponse<T>(response: any): T {
    return response.data;
  }

  protected handleError(error: AxiosError): never {
    if (error.response) {
      const errorData = error.response.data as { message?: string; error?: string };
      throw new Error(errorData.message || errorData.error || 'An error occurred');
    }
    throw error;
  }

  protected async retryRequest<T>(request: () => Promise<T>): Promise<T> {
    let retries = 0;
    let backoff = BaseService.INITIAL_BACKOFF;

    while (retries < BaseService.MAX_RETRIES) {
      try {
        return await request();
      } catch (error) {
        retries++;
        if (retries === BaseService.MAX_RETRIES) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, backoff));
        backoff *= BaseService.BACKOFF_MULTIPLIER;
      }
    }

    throw new Error('Maximum retries exceeded');
  }
} 