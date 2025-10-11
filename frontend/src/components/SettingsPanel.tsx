import React from 'react';
import { AuthUser } from '../types';

interface SettingsPanelProps {
  user: AuthUser;
  onLogout: () => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  user,
  onLogout,
}: SettingsPanelProps) => {
  const getRoleLabel = (role: string): string => {
    const roleMap: Record<string, string> = {
      student: 'Estudiante',
      teacher: 'Profesor',
      admin: 'Administrador',
    };
    return roleMap[role] || role;
  };

  return (
    <div className="settings-section">
      <h3 className="settings-title">Mi Cuenta</h3>
      <div className="user-info">
        <div className="user-info-item">
          <label className="user-info-label">Nombre</label>
          <p className="user-info-value">{user.name}</p>
        </div>
        <div className="user-info-item">
          <label className="user-info-label">Email</label>
          <p className="user-info-value">{user.email}</p>
        </div>
        <div className="user-info-item">
          <label className="user-info-label">Rol</label>
          <p className="user-info-value">{getRoleLabel(user.role)}</p>
        </div>
      </div>
      <button 
        className="logout-button"
        onClick={onLogout}
      >
        Cerrar Sesión
      </button>
    </div>
  );
};

export default SettingsPanel;
