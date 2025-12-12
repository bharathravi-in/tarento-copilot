// User and Auth types
export interface User {
  id: string;
  email: string;
  full_name: string;
  organization_id: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthToken;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Generic response types
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  skip?: number;
  limit?: number;
}

// Document types
export interface Document {
  id: string;
  title: string;
  summary: string;
  content: string;
  source: string;
  tags: string[];
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDocumentRequest {
  title: string;
  summary: string;
  content: string;
  source?: string;
  tags?: string[];
}

export interface UpdateDocumentRequest {
  title?: string;
  summary?: string;
  content?: string;
  source?: string;
  tags?: string[];
}

export interface DocumentSearchRequest {
  query: string;
  limit?: number;
  score_threshold?: number;
}

export interface DocumentSearchResult {
  id: string;
  title: string;
  summary: string;
  content_preview: string;
  relevance_score: number;
}

// Conversation types
export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CreateConversationRequest {
  title: string;
}

export interface UpdateConversationRequest {
  title?: string;
}

export interface CreateMessageRequest {
  role: 'user' | 'assistant';
  content: string;
}

export interface MessageSearchRequest {
  query: string;
  limit?: number;
  score_threshold?: number;
}

export interface MessageSearchResult {
  id: string;
  content: string;
  relevance_score: number;
  role: 'user' | 'assistant';
}

// Agent types
export interface Agent {
  id: string;
  name: string;
  description: string;
  system_prompt: string;
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  description: string;
  system_prompt: string;
}

export interface UpdateAgentRequest {
  name?: string;
  description?: string;
  system_prompt?: string;
}

export interface ExecuteAgentRequest {
  prompt: string;
  conversation_id?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ExecuteAgentWithRAGRequest {
  prompt: string;
  conversation_id?: string;
  document_limit?: number;
  score_threshold?: number;
  temperature?: number;
  max_tokens?: number;
}

export interface ContextDocument {
  id: string;
  title: string;
  preview: string;
  relevance_score: number;
}

export interface ContextMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  relevance_score: number;
}

export interface RAGContext {
  documents: ContextDocument[];
  messages: ContextMessage[];
  summary: string;
}

export interface ExecuteAgentWithFullRAGRequest {
  prompt: string;
  conversation_id?: string;
  retrieve_documents?: boolean;
  document_limit?: number;
  document_score_threshold?: number;
  retrieve_conversation_context?: boolean;
  message_limit?: number;
  message_score_threshold?: number;
  temperature?: number;
  max_tokens?: number;
}

export interface ExecuteAgentResponse {
  response: string;
  execution_time_ms: number;
}

export interface ExecuteAgentWithRAGResponse extends ExecuteAgentResponse {
  context_documents: ContextDocument[];
  context_text: string;
  document_count: number;
}

export interface ExecuteAgentWithFullRAGResponse extends ExecuteAgentResponse {
  context: RAGContext;
  document_count: number;
  message_count: number;
}
