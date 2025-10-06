/**
 * LTIStateDisplay Component
 * 
 * Displays loading and error states for LTI session validation.
 * Extracted from App.tsx to separate LTI-specific UI concerns.
 */

interface LTIStateDisplayProps {
  loading: boolean;
  error: string | null;
}

export default function LTIStateDisplay({ loading, error }: LTIStateDisplayProps) {
  if (loading) {
    return (
      <div className="lti-loading">
        <div className="lti-loading-spinner"></div>
        <div className="lti-loading-text">Loading session...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lti-error">
        <div className="lti-error-icon">⚠️</div>
        <h2 className="lti-error-title">Session Error</h2>
        <p className="lti-error-message">{error}</p>
      </div>
    );
  }

  return null;
}
