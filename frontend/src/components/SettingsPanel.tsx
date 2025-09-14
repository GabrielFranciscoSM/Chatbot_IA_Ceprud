import React from 'react';
import { UserSettings } from '../types';
import { validateEmail, formatUGREmail } from '../utils';

interface SettingsPanelProps {
  userSettings: UserSettings;
  onSettingsChange: (settings: UserSettings) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  userSettings,
  onSettingsChange,
}: SettingsPanelProps) => {
  const handleEmailChange = (email: string) => {
    const formattedEmail = formatUGREmail(email);
    onSettingsChange({
      ...userSettings,
      email: formattedEmail,
    });
  };

  const isValidEmail = validateEmail(userSettings.email);

  return (
    <div className="settings-section">
      <h3 className="settings-title">Configuración</h3>
      <div className="settings-form">
        <div className="form-group">
          <label className="form-label">Email UGR</label>
          <input
            type="email"
            className="form-input"
            value={userSettings.email}
            onChange={(e) => handleEmailChange(e.target.value)}
            placeholder="tu.email@correo.ugr.es"
          />
          {userSettings.email && !isValidEmail && (
            <span className="error-text">Email inválido</span>
          )}
          <small className="form-help">
            Tu email se usa para gestionar las sesiones de chat por asignatura.
          </small>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
