/**
 * useChatHandling Hook
 * 
 * Manages chat message sending and state updates.
 * Extracted from App.tsx to separate chat handling logic.
 */

import { useState } from 'react';
import { Session, ChatRequest } from '../types';
import { chatApi } from '../api';
import {
  addMessageToSession,
  createMessage,
  validateEmail,
  formatRetryAfter
} from '../utils';

interface UseChatHandlingProps {
  currentSession: Session | null;
  selectedSubject: string;
  userEmail: string;
  sessions: Session[];
  setSessions: (sessions: Session[]) => void;
  setCurrentSession: (session: Session) => void;
}

export function useChatHandling({
  currentSession,
  selectedSubject,
  userEmail,
  sessions,
  setSessions,
  setCurrentSession
}: UseChatHandlingProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [rateLimitInfo, setRateLimitInfo] = useState<any>(null);

  const handleSendMessage = async (messageContent: string) => {
    if (!currentSession || !validateEmail(userEmail)) {
      setError('Por favor, introduce un email válido antes de enviar mensajes.');
      return;
    }

    setError('');
    setRateLimitInfo(null);
    setIsLoading(true);

    // Add user message
    const userMessage = createMessage(messageContent, 'user', selectedSubject);
    const updatedSession = addMessageToSession(currentSession, userMessage);
    
    // Update sessions
    const newSessions = sessions.map(s => 
      s.id === updatedSession.id ? updatedSession : s
    );
    setSessions(newSessions);
    setCurrentSession(updatedSession);

    try {
      const request: ChatRequest = {
        message: messageContent,
        subject: selectedSubject,
        mode: 'rag',
        email: userEmail
      };

      const response = await chatApi.sendMessage(request);
      
      // Add assistant response with sources and model info
      const assistantMessage = createMessage(
        response.response, 
        'assistant', 
        selectedSubject,
        response.sources,
        response.model_used
      );
      const finalSession = addMessageToSession(updatedSession, assistantMessage);
      
      // Update sessions
      const finalSessions = newSessions.map(s => 
        s.id === finalSession.id ? finalSession : s
      );
      setSessions(finalSessions);
      setCurrentSession(finalSession);

    } catch (err: any) {
      console.error('Chat error:', err);
      
      if (err.type === 'RATE_LIMIT') {
        setRateLimitInfo(err.data);
        setError(`Límite de mensajes alcanzado. Intenta de nuevo en ${formatRetryAfter(err.data.retry_after || 60)}.`);
      } else {
        setError(err.message || 'Error al enviar el mensaje. Por favor, inténtalo de nuevo.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    rateLimitInfo,
    setError,
    setRateLimitInfo,
    handleSendMessage
  };
}
