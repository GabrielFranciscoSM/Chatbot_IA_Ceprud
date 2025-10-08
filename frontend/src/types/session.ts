/**
 * Session Types for LTI Integration
 * 
 * Defines TypeScript interfaces for session management in LTI mode.
 */

export interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
}

export interface SessionData {
  sessionToken: string | null;
  isLTI: boolean;
  subject: string | null;
  user: User | null;
  contextLabel: string | null; // Moodle course short name
  validated: boolean;
  loading: boolean;
  error: string | null;
}

export interface SessionContextType extends SessionData {
  validateSession: (token: string) => Promise<void>;
  clearSession: () => void;
}

export interface SessionValidationResponse {
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  subject: string;
  context_label: string;
}
