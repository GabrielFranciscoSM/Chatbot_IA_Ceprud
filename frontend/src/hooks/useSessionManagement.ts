/**
 * useSessionManagement Hook
 * 
 * Manages session state including loading from storage and creating new sessions.
 * Extracted from App.tsx to separate session management logic.
 */

import { useState, useEffect, useRef } from 'react';
import { Session, UserSettings } from '../types';
import { SUBJECTS } from '../constants';
import {
  loadSessionsFromStorage,
  saveSessionsToStorage,
  loadUserSettings,
  saveUserSettings,
  loadSelectedSubject,
  saveSelectedSubject,
  findOrCreateSession,
  cleanOldSessions,
  validateEmail
} from '../utils';

interface UseSessionManagementProps {
  sessionContext: any; // LTI session context
  loadUserSubjects: (email: string) => Promise<void>;
}

export function useSessionManagement({ sessionContext, loadUserSubjects }: UseSessionManagementProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [userSettings, setUserSettings] = useState<UserSettings>({
    email: ''
  });

  // Use ref to track if initial load has happened
  const initialLoadDone = useRef(false);

  // Load initial data - only runs once
  useEffect(() => {
    if (initialLoadDone.current) return;
    initialLoadDone.current = true;

    const savedSessions = loadSessionsFromStorage();
    const savedSettings = loadUserSettings();
    const savedSubject = loadSelectedSubject();

    setSessions(cleanOldSessions(savedSessions));
    setUserSettings(savedSettings);
    
    // If LTI mode, use session user data
    if (sessionContext.isLTI && sessionContext.validated && sessionContext.user) {
      console.log('App: LTI mode detected, using session user', sessionContext.user);
      setUserSettings({
        email: sessionContext.user.email,
      });
      
      // Set subject from LTI session if available
      if (sessionContext.subject) {
        setSelectedSubject(sessionContext.subject);
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
    // Only run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update current session when subject or email changes
  useEffect(() => {
    if (selectedSubject && userSettings.email) {
      const session = findOrCreateSession(sessions, selectedSubject, userSettings.email);
      setCurrentSession(session);
      
      // Add session to sessions if it's new
      const existingSession = sessions.find(s => s.id === session.id);
      if (!existingSession) {
        const newSessions = [...sessions, session];
        setSessions(newSessions);
      }
      
      saveSelectedSubject(selectedSubject);
    } else if (selectedSubject) {
      // If no email yet, just update the subject but don't create session
      saveSelectedSubject(selectedSubject);
      setCurrentSession(null);
    }
    // Don't include sessions in dependencies to avoid infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSubject, userSettings.email]);

  // Save sessions when they change
  useEffect(() => {
    if (initialLoadDone.current) {
      saveSessionsToStorage(sessions);
    }
  }, [sessions]);

  // Save user settings when they change
  useEffect(() => {
    if (initialLoadDone.current) {
      saveUserSettings(userSettings);
    }
  }, [userSettings]);

  return {
    sessions,
    setSessions,
    selectedSubject,
    setSelectedSubject,
    currentSession,
    setCurrentSession,
    userSettings,
    setUserSettings
  };
}
