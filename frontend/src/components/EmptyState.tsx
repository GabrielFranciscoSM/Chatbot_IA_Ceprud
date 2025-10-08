/**
 * EmptyState Component
 * 
 * Displays a friendly message when no subject is selected or no messages exist.
 * Extracted from App.tsx to separate empty state UI.
 */

export default function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">🎓</div>
      <h3 className="empty-state-title">Bienvenido al Chatbot UGR</h3>
      <p className="empty-state-description">
        Selecciona una asignatura para comenzar a chatear.
      </p>
    </div>
  );
}
