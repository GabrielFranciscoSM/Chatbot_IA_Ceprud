/**
 * Session Context for LTI Integration
 * 
 * Manages session state for LTI launches from Moodle.
 * Handles session token validation and user authentication.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SessionContextType, SessionData } from '../types/session';
import { chatApi } from '../api';

const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  children: ReactNode;
}

export const SessionProvider = ({ children }: SessionProviderProps) => {
  const [sessionData, setSessionData] = useState<SessionData>({
    sessionToken: null,
    isLTI: false,
    subject: null,
    user: null,
    contextLabel: null,
    validated: false,
    loading: false,
    error: null,
  });

  /**
   * Parse URL parameters on mount to check for LTI session
   */
  useEffect(() => {
    const parseURLParameters = async () => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get('session_token');
      const lti = params.get('lti') === 'true';
      const subject = params.get('subject');

      console.log('SessionContext: Parsing URL parameters', { token: !!token, lti, subject });

      if (token && lti) {
        // LTI mode detected
        console.log('SessionContext: LTI mode detected, validating session...');
        
        // Store in localStorage for persistence
        localStorage.setItem('session_token', token);
        if (subject) {
          localStorage.setItem('lti_subject', subject);
        }

        // Update state and validate
        setSessionData(prev => ({
          ...prev,
          sessionToken: token,
          isLTI: true,
          subject: subject,
          loading: true,
        }));

        // Validate session with backend
        await validateSession(token);
      } else {
        // Check localStorage for existing session
        const storedToken = localStorage.getItem('session_token');
        const storedSubject = localStorage.getItem('lti_subject');

        if (storedToken) {
          console.log('SessionContext: Found stored session token, validating...');
          setSessionData(prev => ({
            ...prev,
            sessionToken: storedToken,
            isLTI: true,
            subject: storedSubject,
            loading: true,
          }));

          await validateSession(storedToken);
        }
      }
    };

    parseURLParameters();
  }, []);

  /**
   * Validate session token with backend
   */
  const validateSession = async (token: string) => {
    try {
      console.log('SessionContext: Validating session token...');
      
      const response = await chatApi.validateSession(token);
      
      console.log('SessionContext: Session validated successfully', response);

      setSessionData(prev => ({
        ...prev,
        user: {
          id: response.user.id,
          name: response.user.name,
          email: response.user.email,
          role: response.user.role,
        },
        subject: response.subject || prev.subject,
        contextLabel: response.context_label,
        validated: true,
        loading: false,
        error: null,
      }));
    } catch (error: any) {
      console.error('SessionContext: Session validation failed', error);
      
      // Clear invalid session
      localStorage.removeItem('session_token');
      localStorage.removeItem('lti_subject');

      setSessionData(prev => ({
        ...prev,
        sessionToken: null,
        isLTI: false,
        validated: false,
        loading: false,
        error: error.message || 'Session validation failed',
      }));
    }
  };

  /**
   * Clear session (logout)
   */
  const clearSession = () => {
    console.log('SessionContext: Clearing session');
    
    localStorage.removeItem('session_token');
    localStorage.removeItem('lti_subject');

    setSessionData({
      sessionToken: null,
      isLTI: false,
      subject: null,
      user: null,
      contextLabel: null,
      validated: false,
      loading: false,
      error: null,
    });
  };

  const contextValue: SessionContextType = {
    ...sessionData,
    validateSession,
    clearSession,
  };

  return (
    <SessionContext.Provider value={contextValue}>
      {children}
    </SessionContext.Provider>
  );
};

/**
 * Hook to use session context
 */
export const useSessionContext = () => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSessionContext must be used within a SessionProvider');
  }
  return context;
};
