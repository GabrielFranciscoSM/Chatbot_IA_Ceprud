import React from 'react';
import { Subject } from '../types';
import { SUBJECTS } from '../constants';

interface SubjectSidebarProps {
  selectedSubject: string;
  onSubjectChange: (subject: string) => void;
}

const SubjectSidebar: React.FC<SubjectSidebarProps> = ({
  selectedSubject,
  onSubjectChange,
}) => {
  return (
    <div className="subjects-section">
      <h3 className="subjects-title">Asignaturas</h3>
      <div className="subject-list">
        {SUBJECTS.map((subject: Subject) => (
          <div
            key={subject.id}
            className={`subject-item ${selectedSubject === subject.id ? 'active' : ''}`}
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
        ))}
      </div>
    </div>
  );
};

export default SubjectSidebar;
