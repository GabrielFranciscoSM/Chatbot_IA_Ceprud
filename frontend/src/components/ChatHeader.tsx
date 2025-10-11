/**
 * ChatHeader Component
 * 
 * Displays the current subject information and chat actions.
 * Extracted from App.tsx to separate header concerns.
 */

import { Subject } from '../types';

interface ChatHeaderProps {
  selectedSubjectInfo: Subject | undefined;
}

export default function ChatHeader({ selectedSubjectInfo }: ChatHeaderProps) {
  return (
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
        {/* Future: Add clear conversation button here */}
      </div>
    </div>
  );
}
