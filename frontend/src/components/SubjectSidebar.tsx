import React from 'react';
import { Subject } from '../types';
import { SUBJECTS } from '../constants';
import SubjectSearch from './SubjectSearch';

interface SubjectSidebarProps {
  selectedSubject: string;
  onSubjectChange: (subject: string) => void;
  userSubjects: string[];
  onAddSubject: (subjectId: string) => Promise<void>;
  onRemoveSubject: (subjectId: string) => Promise<void>;
}

const SubjectSidebar: React.FC<SubjectSidebarProps> = ({
  selectedSubject,
  onSubjectChange,
  userSubjects,
  onAddSubject,
  onRemoveSubject,
}) => {
  // Filter SUBJECTS to only show those that the user has
  const userSubjectsList = SUBJECTS.filter(subject => 
    userSubjects.includes(subject.id)
  );

  return (
    <div className="subjects-section">
      <h3 className="subjects-title">Mis Asignaturas</h3>
      
      {/* Search bar to add new subjects */}
      <SubjectSearch 
        userSubjects={userSubjects}
        onAddSubject={onAddSubject}
      />

      {/* User's subjects list */}
      <div className="subject-list">
        {userSubjectsList.length > 0 ? (
          userSubjectsList.map((subject: Subject) => (
            <div
              key={subject.id}
              className={`subject-item ${selectedSubject === subject.id ? 'active' : ''}`}
            >
              <div 
                className="subject-clickable"
                onClick={() => onSubjectChange(subject.id)}
              >
                <span className="subject-icon">{subject.icon}</span>
                <div className="subject-info">
                  <div className="subject-name">{subject.name}</div>
                  {subject.description && (
                    <div className="subject-description">{subject.description}</div>
                  )}
                </div>
              </div>
              <button 
                className="remove-subject-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveSubject(subject.id);
                }}
                title="Eliminar asignatura"
              >
                ×
              </button>
            </div>
          ))
        ) : (
          <div className="no-subjects-message">
            No tienes asignaturas añadidas.
            <br />
            Usa el buscador para añadir una.
          </div>
        )}
      </div>
    </div>
  );
};

export default SubjectSidebar;
