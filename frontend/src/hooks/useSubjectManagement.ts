/**
 * useSubjectManagement Hook
 * 
 * Manages user subjects including loading, adding, and removing subjects.
 * Extracted from App.tsx to separate subject management concerns.
 */

import { useState, useEffect, useCallback } from 'react';
import { chatApi } from '../api';
import { validateEmail } from '../utils';

interface UseSubjectManagementProps {
  userEmail: string;
  selectedSubject: string;
  setSelectedSubject: (subject: string) => void;
  setError: (error: string) => void;
}

export function useSubjectManagement({ 
  userEmail, 
  selectedSubject, 
  setSelectedSubject, 
  setError 
}: UseSubjectManagementProps) {
  const [userSubjects, setUserSubjects] = useState<string[]>([]);

  // Load user subjects from API - memoized to prevent infinite loops
  const loadUserSubjects = useCallback(async (email: string) => {
    try {
      const response = await chatApi.getUserSubjects(email);
      if (response.success) {
        setUserSubjects(response.subjects);
        // Don't auto-select here - let the parent component handle it
      }
    } catch (error) {
      console.error('Error loading user subjects:', error);
    }
  }, []); // No dependencies - this function is stable

  // Load subjects when email changes and is valid
  useEffect(() => {
    if (userEmail && validateEmail(userEmail)) {
      loadUserSubjects(userEmail);
    }
  }, [userEmail, loadUserSubjects]);

  const handleAddSubject = useCallback(async (subjectId: string) => {
    if (!validateEmail(userEmail)) {
      setError('Por favor, introduce un email válido para añadir asignaturas.');
      return;
    }

    try {
      const response = await chatApi.addSubjectToUser(userEmail, subjectId);
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
  }, [userEmail, setError, setSelectedSubject]);

  const handleRemoveSubject = useCallback(async (subjectId: string) => {
    if (!validateEmail(userEmail)) {
      return;
    }

    try {
      const response = await chatApi.removeSubjectFromUser(userEmail, subjectId);
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
  }, [userEmail, selectedSubject, setError, setSelectedSubject]);

  return {
    userSubjects,
    handleAddSubject,
    handleRemoveSubject,
    loadUserSubjects
  };
}
