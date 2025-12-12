import { logger } from './logger';

export interface ApiErrorResponse {
  detail: string | unknown;
  status?: number;
  timestamp?: string;
}

export class ApiError extends Error {
  declare public status: number;
  declare public details?: unknown;

  constructor(
    status: number,
    message: string,
    details?: unknown
  ) {
    super(message);
    this.status = status;
    this.details = details;
    this.name = 'ApiError';
  }
}

export class NetworkError extends Error {
  constructor(message: string = 'Network error occurred') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  declare public fields: Record<string, string[]>;

  constructor(
    fields: Record<string, string[]>,
    message: string = 'Validation failed'
  ) {
    super(message);
    this.fields = fields;
    this.name = 'ValidationError';
  }
}

/**
 * Parse error response from API
 */
export function parseApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof Error) {
    // Handle axios errors
    const axiosError = error as any;
    
    if (axiosError.response) {
      const { status, data } = axiosError.response;
      const errorData = data as ApiErrorResponse;
      
      logger.error('API Error Response', { status, data });
      
      if (status === 422) {
        // Validation error
        const fields: Record<string, string[]> = {};
        if (Array.isArray(errorData.detail)) {
          errorData.detail.forEach((err: any) => {
            const field = err.loc?.[1] || 'unknown';
            if (!fields[field]) fields[field] = [];
            fields[field].push(err.msg);
          });
        }
        throw new ValidationError(fields, 'Validation failed');
      }
      
      return new ApiError(
        status,
        typeof errorData.detail === 'string' 
          ? errorData.detail 
          : 'An error occurred',
        errorData.detail
      );
    }

    if (axiosError.request && !axiosError.response) {
      logger.error('Network Error', { message: error.message });
      throw new NetworkError(error.message);
    }

    logger.error('Unknown Error', { message: error.message });
    return new ApiError(500, error.message);
  }

  logger.error('Unexpected Error', error);
  return new ApiError(500, 'An unexpected error occurred');
}

/**
 * Format error message for display
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ValidationError) {
    const messages = Object.values(error.fields).flat();
    return messages[0] || 'Validation failed';
  }

  if (error instanceof ApiError) {
    if (error.status === 401) return 'Unauthorized. Please login again.';
    if (error.status === 403) return 'You do not have permission to perform this action.';
    if (error.status === 404) return 'Resource not found.';
    if (error.status === 409) return 'Conflict. The resource may have been modified.';
    if (error.status === 500) return 'Server error. Please try again later.';
    return error.message || 'An error occurred';
  }

  if (error instanceof NetworkError) {
    return 'Network error. Please check your connection.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
}
