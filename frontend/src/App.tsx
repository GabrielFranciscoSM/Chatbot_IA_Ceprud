import './styles/App.css';
import { useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { useSession } from './hooks/useSession';
import { useSessionManagement } from './hooks/useSessionManagement';
import { useSubjectManagement } from './hooks/useSubjectManagement';
import { useChatHandling } from './hooks/useChatHandling';

// Components
import LoginRegister from './components/LoginRegister';
import SubjectSidebar from './components/SubjectSidebar';
import SettingsPanel from './components/SettingsPanel';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import ErrorDisplay from './components/ErrorDisplay';
import LTIStateDisplay from './components/LTIStateDisplay';
import ChatHeader from './components/ChatHeader';
import EmptyState from './components/EmptyState';
import ContextBanner from './components/ContextBanner';

// Types and Utils
import { SUBJECTS } from './constants';

function App() {
  const { user, login, logout, isAuthenticated } = useAuth();
  const [authError, setAuthError] = useState('');
  
  // Session context for LTI integration
  const session = useSession();
  
  // Session management hook (state + persistence)
  const {
    sessions,
    setSessions,
    selectedSubject,
    setSelectedSubject,
    currentSession,
    setCurrentSession,
    userSettings,
    setUserSettings
  } = useSessionManagement({ 
    sessionContext: session,
    loadUserSubjects: async () => {}, // Will be replaced below
    userEmail: user?.email
  });

  // Chat handling hook (messages + API)
  const {
    isLoading,
    error,
    rateLimitInfo,
    setError,
    setRateLimitInfo,
    handleSendMessage
  } = useChatHandling({
    currentSession,
    selectedSubject,
    userEmail: user?.email || userSettings.email,
    sessions,
    setSessions,
    setCurrentSession
  });

  // Subject management hook
  const subjectManagement = useSubjectManagement({
    userEmail: user?.email || userSettings.email,
    selectedSubject,
    setSelectedSubject,
    setError
  });

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubject(subjectId);
    setError('');
    setRateLimitInfo(null);
  };

  const handleLogout = () => {
    logout();
    setSelectedSubject('');
    setSessions([]);
    setCurrentSession(null);
  };

  const handleLogin = (email: string, name: string, userId: string, role: string) => {
    login(email, name, userId, role);
    setAuthError('');
    // Update user settings with authenticated email
    setUserSettings({ email });
  };

  const selectedSubjectInfo = SUBJECTS.find(s => s.id === selectedSubject);

  // Show loading state while validating LTI session
  if (session.isLTI && (session.loading || session.error)) {
    return <LTIStateDisplay loading={session.loading} error={session.error} />;
  }

  // Show login/register screen if not authenticated and not in LTI mode
  if (!isAuthenticated && !session.isLTI) {
    return (
      <>
        <LoginRegister 
          onLogin={handleLogin}
          onError={setAuthError}
        />
        {authError && (
          <div className="auth-error-overlay">
            <div className="auth-error-message">
              {authError}
            </div>
          </div>
        )}
      </>
    );
  }

  return (
    <div className={session.isLTI ? "app lti-mode" : "app"}>
      {/* Sidebar - Hidden in LTI mode */}
      {!session.isLTI && user && (
        <div className="sidebar">
          <div className="sidebar-header">
            <h1 className="sidebar-title">Chatbot UGR</h1>
            <p className="sidebar-subtitle">CEPRUD - Centro de Estudios de Postgrado</p>
          </div>
          
          <SubjectSidebar
            selectedSubject={selectedSubject}
            onSubjectChange={handleSubjectChange}
            userSubjects={subjectManagement.userSubjects}
            onAddSubject={subjectManagement.handleAddSubject}
            onRemoveSubject={subjectManagement.handleRemoveSubject}
          />
          
          <SettingsPanel
            user={user}
            onLogout={handleLogout}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Context Banner for LTI mode */}
        {session.isLTI && session.contextLabel && (
          <ContextBanner contextLabel={session.contextLabel} />
        )}

        {/* Header */}
        <ChatHeader selectedSubjectInfo={selectedSubjectInfo} />

        {/* Error/Rate Limit Messages */}
        <ErrorDisplay error={error} rateLimitInfo={rateLimitInfo} />

        {/* Messages */}
        <div className="chat-messages">
          {selectedSubject && currentSession ? (
            <MessageList
              messages={currentSession.messages}
              isLoading={isLoading}
            />
          ) : (
            <EmptyState />
          )}
        </div>

        {/* Input */}
        {selectedSubject && currentSession && (
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder={
              "Escribe tu pregunta sobre " + (selectedSubjectInfo?.name || "la asignatura") + "..."
            }
          />
        )}
      </div>
    </div>
  );
}

export default App;
