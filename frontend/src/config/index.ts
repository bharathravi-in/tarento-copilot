// Environment configuration
export const config = {
  api: {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  },
  app: {
    name: import.meta.env.VITE_APP_NAME || 'Tarento Copilot',
    logLevel: (import.meta.env.VITE_LOG_LEVEL || 'info') as 'debug' | 'info' | 'warn' | 'error',
  },
};

// Token storage key
export const TOKEN_KEY = 'auth_token';
export const USER_KEY = 'user_info';

// API endpoints
export const API_ENDPOINTS = {
  // Auth
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
  },
  // Documents
  documents: {
    list: '/documents',
    create: '/documents',
    get: (id: string) => `/documents/${id}`,
    update: (id: string) => `/documents/${id}`,
    delete: (id: string) => `/documents/${id}`,
    search: {
      semantic: '/documents/search/semantic',
      hybrid: '/documents/search/hybrid',
    },
  },
  // Conversations
  conversations: {
    list: '/conversations',
    create: '/conversations',
    get: (id: string) => `/conversations/${id}`,
    update: (id: string) => `/conversations/${id}`,
    delete: (id: string) => `/conversations/${id}`,
    messages: {
      list: (id: string) => `/conversations/${id}/messages`,
      create: (id: string) => `/conversations/${id}/messages`,
      delete: (id: string, msgId: string) => `/conversations/${id}/messages/${msgId}`,
      search: (id: string) => `/conversations/${id}/search`,
    },
  },
  // Agents
  agents: {
    list: '/agents',
    create: '/agents',
    get: (id: string) => `/agents/${id}`,
    update: (id: string) => `/agents/${id}`,
    delete: (id: string) => `/agents/${id}`,
    execute: {
      simple: (id: string) => `/agents/${id}/execute`,
      rag: '/agents/execute/rag',
      fullRag: '/agents/execute/full-rag',
    },
  },
} as const;
