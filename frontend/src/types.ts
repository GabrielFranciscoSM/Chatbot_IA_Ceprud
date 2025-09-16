// Types for the application
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  subject?: string;
  sources?: string[];
  modelUsed?: string;
}

export interface Subject {
  id: string;
  name: string;
  icon: string;
  description?: string;
}

export interface ChatRequest {
  message: string;
  subject: string;
  mode: string;
  email: string;
}

export interface ChatResponse {
  response: string;
  subject: string;
  session_id?: string;
  processing_time?: number;
  sources?: string[];
  model_used?: string;
  query_type?: string;
}

export interface Session {
  id: string;
  subject: string;
  email: string;
  messages: Message[];
  lastActivity: Date;
}

export interface RateLimitInfo {
  requests_made: number;
  requests_remaining: number;
  reset_time: number;
  retry_after?: number;
}

export interface ErrorResponse {
  error: string;
  details?: any;
}

export type ChatMode = 'base' | 'rag' | 'rag_lora';

export interface UserSettings {
  email: string;
}
