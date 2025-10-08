/**
 * ErrorDisplay Component
 * 
 * Displays error messages and rate limit information in a consistent way.
 * Extracted from App.tsx to improve readability and reusability.
 */

interface ErrorDisplayProps {
  error: string;
  rateLimitInfo?: {
    requests_made: number;
    requests_remaining: number;
    reset_time: number;
  } | null;
}

export default function ErrorDisplay({ error, rateLimitInfo }: ErrorDisplayProps) {
  if (!error) return null;

  return (
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
  );
}
