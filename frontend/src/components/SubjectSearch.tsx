import React, { useState, useMemo } from 'react';
import { Subject } from '../types';
import { SUBJECTS } from '../constants';

interface SubjectSearchProps {
  userSubjects: string[];
  onAddSubject: (subjectId: string) => Promise<void>;
}

const SubjectSearch: React.FC<SubjectSearchProps> = ({ userSubjects, onAddSubject }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  // Filter subjects that are not already added by the user
  const availableSubjects = useMemo(() => {
    return SUBJECTS.filter(subject => !userSubjects.includes(subject.id));
  }, [userSubjects]);

  // Filter subjects based on search term
  const filteredSubjects = useMemo(() => {
    if (!searchTerm.trim()) {
      return availableSubjects;
    }
    const term = searchTerm.toLowerCase();
    return availableSubjects.filter(subject =>
      subject.name.toLowerCase().includes(term) ||
      subject.description?.toLowerCase().includes(term)
    );
  }, [availableSubjects, searchTerm]);

  const handleAddSubject = async (subjectId: string) => {
    setIsAdding(true);
    try {
      await onAddSubject(subjectId);
      setSearchTerm(''); // Clear search after adding
    } catch (error) {
      console.error('Error adding subject:', error);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="subject-search-container">
      <div className="search-input-wrapper">
        <input
          type="text"
          className="subject-search-input"
          placeholder="Buscar asignaturas..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setIsSearching(true)}
        />
        <span className="search-icon">🔍</span>
      </div>

      {isSearching && searchTerm.trim() && (
        <div className="search-results">
          {filteredSubjects.length > 0 ? (
            <>
              <div className="search-results-header">
                {filteredSubjects.length} asignatura{filteredSubjects.length !== 1 ? 's' : ''} disponible{filteredSubjects.length !== 1 ? 's' : ''}
              </div>
              {filteredSubjects.map((subject: Subject) => (
                <div
                  key={subject.id}
                  className="search-result-item"
                  onClick={() => !isAdding && handleAddSubject(subject.id)}
                >
                  <span className="subject-icon">{subject.icon}</span>
                  <div className="subject-info">
                    <div className="subject-name">{subject.name}</div>
                    {subject.description && (
                      <div className="subject-description">{subject.description}</div>
                    )}
                  </div>
                  <button 
                    className="add-subject-btn"
                    disabled={isAdding}
                  >
                    {isAdding ? '...' : '+'}
                  </button>
                </div>
              ))}
            </>
          ) : (
            <div className="no-results">
              No se encontraron asignaturas
            </div>
          )}
        </div>
      )}

      {isSearching && !searchTerm.trim() && availableSubjects.length > 0 && (
        <div className="search-results">
          <div className="search-results-header">
            Todas las asignaturas disponibles
          </div>
          {availableSubjects.map((subject: Subject) => (
            <div
              key={subject.id}
              className="search-result-item"
              onClick={() => !isAdding && handleAddSubject(subject.id)}
            >
              <span className="subject-icon">{subject.icon}</span>
              <div className="subject-info">
                <div className="subject-name">{subject.name}</div>
                {subject.description && (
                  <div className="subject-description">{subject.description}</div>
                )}
              </div>
              <button 
                className="add-subject-btn"
                disabled={isAdding}
              >
                {isAdding ? '...' : '+'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Close search overlay when clicking outside */}
      {isSearching && (
        <div 
          className="search-overlay"
          onClick={() => setIsSearching(false)}
        />
      )}
    </div>
  );
};

export default SubjectSearch;
