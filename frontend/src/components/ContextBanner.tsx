/**
 * ContextBanner Component
 * 
 * Displays context information for LTI mode (Moodle course).
 * Extracted from App.tsx to separate LTI context display.
 */

interface ContextBannerProps {
  contextLabel: string;
}

export default function ContextBanner({ contextLabel }: ContextBannerProps) {
  return (
    <div className="context-banner">
      <span className="context-banner-icon">📚</span>
      <div className="context-banner-text">
        <div className="context-banner-label">Moodle Course</div>
        <div className="context-banner-course">{contextLabel}</div>
      </div>
    </div>
  );
}
