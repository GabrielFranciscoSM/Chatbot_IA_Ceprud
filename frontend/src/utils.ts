import { v4 as uuidv4 } from 'uuid';
import { Session, Message, UserSettings } from './types';
import { SESSION_STORAGE_KEYS, DEFAULT_EMAIL_DOMAIN } from './constants';

// Session Management
export const createSession = (subject: string, email: string): Session => ({
  id: uuidv4(),
  subject,
  email,
  messages: [],
  lastActivity: new Date()
});

export const saveSessionsToStorage = (sessions: Session[]): void => {
  try {
    localStorage.setItem(SESSION_STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
  } catch (error) {
    console.error('Failed to save sessions to localStorage:', error);
  }
};

export const loadSessionsFromStorage = (): Session[] => {
  try {
    const sessionsData = localStorage.getItem(SESSION_STORAGE_KEYS.SESSIONS);
    if (!sessionsData) return [];
    
    const sessions = JSON.parse(sessionsData);
    // Convert date strings back to Date objects
    return sessions.map((session: any) => ({
      ...session,
      lastActivity: new Date(session.lastActivity),
      messages: session.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    }));
  } catch (error) {
    console.error('Failed to load sessions from localStorage:', error);
    return [];
  }
};

export const findOrCreateSession = (sessions: Session[], subject: string, email: string): Session => {
  const existingSession = sessions.find(s => s.subject === subject && s.email === email);
  if (existingSession) {
    existingSession.lastActivity = new Date();
    return existingSession;
  }
  
  return createSession(subject, email);
};

export const addMessageToSession = (session: Session, message: Message): Session => {
  return {
    ...session,
    messages: [...session.messages, message],
    lastActivity: new Date()
  };
};

export const cleanOldSessions = (sessions: Session[], maxAge: number = 24 * 60 * 60 * 1000): Session[] => {
  const cutoffTime = new Date(Date.now() - maxAge);
  return sessions.filter(session => session.lastActivity > cutoffTime);
};

// Message Creation
export const createMessage = (
  content: string, 
  role: 'user' | 'assistant', 
  subject?: string, 
  sources?: string[], 
  modelUsed?: string
): Message => ({
  id: uuidv4(),
  content,
  role,
  timestamp: new Date(),
  subject,
  sources,
  modelUsed
});

// User Settings Management
export const saveUserSettings = (settings: UserSettings): void => {
  try {
    localStorage.setItem(SESSION_STORAGE_KEYS.USER_EMAIL, settings.email);
  } catch (error) {
    console.error('Failed to save user settings:', error);
  }
};

export const loadUserSettings = (): UserSettings => {
  try {
    const email = localStorage.getItem(SESSION_STORAGE_KEYS.USER_EMAIL) || '';
    
    return { email };
  } catch (error) {
    console.error('Failed to load user settings:', error);
    return { email: '' };
  }
};

export const saveSelectedSubject = (subject: string): void => {
  try {
    localStorage.setItem(SESSION_STORAGE_KEYS.SELECTED_SUBJECT, subject);
  } catch (error) {
    console.error('Failed to save selected subject:', error);
  }
};

export const loadSelectedSubject = (): string => {
  try {
    return localStorage.getItem(SESSION_STORAGE_KEYS.SELECTED_SUBJECT) || '';
  } catch (error) {
    console.error('Failed to load selected subject:', error);
    return '';
  }
};

// Email Validation
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const formatUGREmail = (email: string): string => {
  if (!email.includes('@')) {
    return `${email}${DEFAULT_EMAIL_DOMAIN}`;
  }
  return email;
};

// Utility Functions
export const formatTimestamp = (date: Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date);
};

export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

// Rate Limiting Helpers
export const formatRetryAfter = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds} segundos`;
  }
  const minutes = Math.ceil(seconds / 60);
  return `${minutes} minuto${minutes > 1 ? 's' : ''}`;
};

export const isRateLimited = (resetTime: number): boolean => {
  return Date.now() / 1000 < resetTime;
};
