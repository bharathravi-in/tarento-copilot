import { apiClient } from './apiClient';
import { API_ENDPOINTS, TOKEN_KEY, USER_KEY } from '../config';
import type { User, AuthToken, LoginRequest, AuthResponse } from '../types/api';
import { logger } from '../utils/logger';

class AuthService {
  /**
   * Login with email and password
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.auth.login,
        credentials
      );

      const { user, tokens } = response.data;

      // Store auth data
      this.setToken(tokens.access_token);
      if (tokens.refresh_token) {
        localStorage.setItem('refresh_token', tokens.refresh_token);
      }
      this.setUser(user);

      logger.info('Login successful', { userId: user.id });
      return response.data;
    } catch (error) {
      logger.error('Login failed', error);
      throw error;
    }
  }

  /**
   * Logout - clear tokens and user data
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.auth.logout);
    } catch (error) {
      logger.warn('Logout API call failed, clearing local state anyway', error);
    } finally {
      this.clearAuth();
      logger.info('Logout successful');
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<AuthToken>(
        API_ENDPOINTS.auth.refresh,
        { refresh_token: refreshToken }
      );

      const newToken = response.data.access_token;
      this.setToken(newToken);

      logger.info('Token refreshed');
      return newToken;
    } catch (error) {
      logger.error('Token refresh failed', error);
      this.clearAuth();
      throw error;
    }
  }

  /**
   * Get current user from local storage
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;

    try {
      return JSON.parse(userStr) as User;
    } catch {
      logger.warn('Failed to parse stored user');
      return null;
    }
  }

  /**
   * Get current token
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getCurrentUser();
  }

  /**
   * Store token
   */
  private setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * Store user
   */
  private setUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Clear all auth data
   */
  private clearAuth(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('refresh_token');
    localStorage.removeItem(USER_KEY);
  }
}

export const authService = new AuthService();
