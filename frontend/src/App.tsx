import { useState, useEffect } from 'react';
// import { Trash2 } from 'lucide-react'; // Temporarily disabled
import './App.css';

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

  // Load initial data
  useEffect(() => {
    const savedSessions = loadSessionsFromStorage();
    const savedSettings = loadUserSettings();
    const savedSubject = loadSelectedSubject();

    setSessions(cleanOldSessions(savedSessions));
    setUserSettings(savedSettings);
    
    if (savedSubject && SUBJECTS.find(s => s.id === savedSubject)) {
      setSelectedSubject(savedSubject);
    } else if (SUBJECTS.length > 0) {
      setSelectedSubject(SUBJECTS[0].id);
    }
  }, []);

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
      
      // Add assistant response
      const assistantMessage = createMessage(response.response, 'assistant', selectedSubject);
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

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Chatbot UGR</h1>
          <p className="sidebar-subtitle">CEPRUD - Centro de Estudios de Postgrado</p>
        </div>
        
        <SubjectSidebar
          selectedSubject={selectedSubject}
          onSubjectChange={handleSubjectChange}
        />
        
        <SettingsPanel
          userSettings={userSettings}
          onSettingsChange={setUserSettings}
        />
      </div>

      {/* Main Content */}
      <div className="main-content">
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
