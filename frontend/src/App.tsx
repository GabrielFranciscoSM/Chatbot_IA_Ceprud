import { useState, useEffect } from 'react';
// import { Trash2 } from 'lucide-react'; // Temporarily disabled
import './App.css';
import { useSession } from './hooks/useSession';

// Components
import SubjectSidebar from './components/SubjectSidebar';
import SettingsPanel from './components/SettingsPanel';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';

// Types and Utils
import { Session, UserSettings, ChatRequest } from './types';
import { SUBJECTS } from './constants';
import { chatApi } from './api';
import {
  loadSessionsFromStorage,
  saveSessionsToStorage,
  loadUserSettings,
  saveUserSettings,
  loadSelectedSubject,
  saveSelectedSubject,
  findOrCreateSession,
  addMessageToSession,
  createMessage,
  cleanOldSessions,
  validateEmail,
  formatRetryAfter
} from './utils';

function App() {
  // Session context for LTI integration
  const session = useSession();
  
  // State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [userSettings, setUserSettings] = useState<UserSettings>({
    email: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [rateLimitInfo, setRateLimitInfo] = useState<any>(null);
  const [userSubjects, setUserSubjects] = useState<string[]>([]);

  // Load initial data
  useEffect(() => {
    const savedSessions = loadSessionsFromStorage();
    const savedSettings = loadUserSettings();
    const savedSubject = loadSelectedSubject();

    setSessions(cleanOldSessions(savedSessions));
    setUserSettings(savedSettings);
    
    // If LTI mode, use session user data
    if (session.isLTI && session.validated && session.user) {
      console.log('App: LTI mode detected, using session user', session.user);
      setUserSettings({
        email: session.user.email,
      });
      
      // Set subject from LTI session if available
      if (session.subject) {
        setSelectedSubject(session.subject);
      }
    } else {
      // Standard mode - load user subjects if email exists
      if (savedSettings.email && validateEmail(savedSettings.email)) {
        loadUserSubjects(savedSettings.email);
      }
      
      if (savedSubject && SUBJECTS.find(s => s.id === savedSubject)) {
        setSelectedSubject(savedSubject);
      }
    }
  }, [session.isLTI, session.validated, session.user, session.subject]);

  // Load user subjects from API
  const loadUserSubjects = async (email: string) => {
    try {
      const response = await chatApi.getUserSubjects(email);
      if (response.success) {
        setUserSubjects(response.subjects);
        // If user has subjects and no subject is selected, select the first one
        if (response.subjects.length > 0 && !selectedSubject) {
          setSelectedSubject(response.subjects[0]);
        }
      }
    } catch (error) {
      console.error('Error loading user subjects:', error);
    }
  };

  // Update current session when subject or email changes
  useEffect(() => {
    if (selectedSubject && userSettings.email) {
      const session = findOrCreateSession(sessions, selectedSubject, userSettings.email);
      setCurrentSession(session);
      
      // Add session to sessions if it's new
      if (!sessions.find(s => s.id === session.id)) {
        const newSessions = [...sessions, session];
        setSessions(newSessions);
        saveSessionsToStorage(newSessions);
      }
      
      saveSelectedSubject(selectedSubject);
    } else if (selectedSubject) {
      // If no email yet, just update the subject but don't create session
      saveSelectedSubject(selectedSubject);
      setCurrentSession(null);
    }
  }, [selectedSubject, userSettings.email, sessions]);

  // Save sessions when they change
  useEffect(() => {
    saveSessionsToStorage(sessions);
  }, [sessions]);

  // Save user settings when they change
  useEffect(() => {
    saveUserSettings(userSettings);
  }, [userSettings]);

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubject(subjectId);
    setError('');
    setRateLimitInfo(null);
  };

  const handleAddSubject = async (subjectId: string) => {
    if (!validateEmail(userSettings.email)) {
      setError('Por favor, introduce un email válido para añadir asignaturas.');
      return;
    }

    try {
      const response = await chatApi.addSubjectToUser(userSettings.email, subjectId);
      if (response.success) {
        setUserSubjects(response.subjects);
        // If this is the first subject, select it automatically
        if (response.subjects.length === 1) {
          setSelectedSubject(subjectId);
        }
      }
    } catch (error: any) {
      console.error('Error adding subject:', error);
      setError('Error al añadir la asignatura. Por favor, inténtalo de nuevo.');
    }
  };

  const handleRemoveSubject = async (subjectId: string) => {
    if (!validateEmail(userSettings.email)) {
      return;
    }

    try {
      const response = await chatApi.removeSubjectFromUser(userSettings.email, subjectId);
      if (response.success) {
        setUserSubjects(response.subjects);
        // If the removed subject was selected, select another one
        if (selectedSubject === subjectId) {
          if (response.subjects.length > 0) {
            setSelectedSubject(response.subjects[0]);
          } else {
            setSelectedSubject('');
          }
        }
      }
    } catch (error: any) {
      console.error('Error removing subject:', error);
      setError('Error al eliminar la asignatura. Por favor, inténtalo de nuevo.');
    }
  };

  const handleSettingsChange = (settings: UserSettings) => {
    setUserSettings(settings);
    // Load subjects when email changes and is valid
    if (validateEmail(settings.email) && settings.email !== userSettings.email) {
      loadUserSubjects(settings.email);
    }
  };

  const handleSendMessage = async (messageContent: string) => {
    if (!currentSession || !validateEmail(userSettings.email)) {
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
        mode: 'rag', // El agente elige automáticamente el mejor modo
        email: userSettings.email
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

  // Temporarily disabled - memory clearing function
  // const handleClearSession = async () => {
  //   if (currentSession && validateEmail(userSettings.email)) {
  //     try {
  //       setIsLoading(true);
  //       setError('');
  //       
  //       // TODO: Backend memory clearing needs improvement
  //       // Temporarily disabled - only clear frontend for now
  //       // await chatApi.clearSession(selectedSubject, userSettings.email);
  //       
  //       // Clear frontend session only
  //       const clearedSession = {
  //         ...currentSession,
  //         messages: []
  //       };
  //       
  //       const newSessions = sessions.map(s => 
  //         s.id === clearedSession.id ? clearedSession : s
  //       );
  //       setSessions(newSessions);
  //       setCurrentSession(clearedSession);
  //       
  //       // Show info message about partial clearing
  //       setError('⚠️ Conversación limpiada (solo interfaz - memoria del bot se conserva temporalmente)');
  //       setTimeout(() => setError(''), 4000);
  //       
  //     } catch (err: any) {
  //       console.error('Error clearing session:', err);
  //       setError('Error al limpiar la conversación. Inténtalo de nuevo.');
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   }
  // };

  const selectedSubjectInfo = SUBJECTS.find(s => s.id === selectedSubject);

  // Show loading state while validating LTI session
  if (session.isLTI && session.loading) {
    return (
      <div className="lti-loading">
        <div className="lti-loading-spinner"></div>
        <div className="lti-loading-text">Loading session...</div>
      </div>
    );
  }

  // Show error state if LTI validation failed
  if (session.isLTI && session.error) {
    return (
      <div className="lti-error">
        <div className="lti-error-icon">⚠️</div>
        <h2 className="lti-error-title">Session Error</h2>
        <p className="lti-error-message">{session.error}</p>
      </div>
    );
  }

  return (
    <div className={session.isLTI ? "app lti-mode" : "app"}>
      {/* Sidebar - Hidden in LTI mode */}
      {!session.isLTI && (
        <div className="sidebar">
          <div className="sidebar-header">
            <h1 className="sidebar-title">Chatbot UGR</h1>
            <p className="sidebar-subtitle">CEPRUD - Centro de Estudios de Postgrado</p>
          </div>
          
          <SubjectSidebar
            selectedSubject={selectedSubject}
            onSubjectChange={handleSubjectChange}
            userSubjects={userSubjects}
            onAddSubject={handleAddSubject}
            onRemoveSubject={handleRemoveSubject}
          />
          
          <SettingsPanel
            userSettings={userSettings}
            onSettingsChange={handleSettingsChange}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Context Banner for LTI mode */}
        {session.isLTI && session.contextLabel && (
          <div className="context-banner">
            <span className="context-banner-icon">📚</span>
            <div className="context-banner-text">
              <div className="context-banner-label">Moodle Course</div>
              <div className="context-banner-course">{session.contextLabel}</div>
            </div>
          </div>
        )}
        {/* Header */}
        <div className="chat-header">
          <div>
            <h2 className="chat-title">
              {selectedSubjectInfo?.icon} {selectedSubjectInfo?.name || 'Selecciona una asignatura'}
            </h2>
            {selectedSubjectInfo?.description && (
              <p className="chat-subtitle">{selectedSubjectInfo.description}</p>
            )}
          </div>
          
          <div className="chat-actions">
            {/* Temporarily hidden - memory clearing needs improvement */}
            {/* {currentSession && currentSession.messages.length > 0 && (
              <button
                className="btn btn-danger"
                onClick={handleClearSession}
                title="Limpiar conversación (solo interfaz)"
              >
                <Trash2 size={16} />
                Limpiar
              </button>
            )} */}
          </div>
        </div>

        {/* Error/Rate Limit Messages */}
        {error && (
          <div className={rateLimitInfo ? "rate-limit-message" : "error-message"}>
            {error}
            {rateLimitInfo && (
              <div style={{ marginTop: '8px', fontSize: '0.75rem' }}>
                <strong>Información del límite:</strong>
                <br />
                Peticiones realizadas: {rateLimitInfo.requests_made}/{rateLimitInfo.requests_made + rateLimitInfo.requests_remaining}
                <br />
                Reinicio: {new Date(rateLimitInfo.reset_time * 1000).toLocaleTimeString()}
              </div>
            )}
          </div>
        )}

        {/* Messages */}
        <div className="chat-messages">
          {selectedSubject && currentSession ? (
            <MessageList
              messages={currentSession.messages}
              isLoading={isLoading}
            />
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">🎓</div>
              <h3 className="empty-state-title">Bienvenido al Chatbot UGR</h3>
              <p className="empty-state-description">
                Selecciona una asignatura para comenzar a chatear.
              </p>
            </div>
          )}
        </div>

        {/* Input */}
        {selectedSubject && currentSession && (
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading || !validateEmail(userSettings.email)}
            placeholder={
              !validateEmail(userSettings.email)
                ? "Introduce tu email UGR para comenzar..."
                : "Escribe tu pregunta sobre " + (selectedSubjectInfo?.name || "la asignatura") + "..."
            }
          />
        )}
      </div>
    </div>
  );
}

export default App;
