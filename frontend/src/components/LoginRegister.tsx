import React, { useState } from 'react';
import { validateEmail } from '../utils';
import '../styles/LoginRegister.css';

interface LoginRegisterProps {
  onLogin: (email: string, name: string, userId: string, role: string) => void;
  onError: (message: string) => void;
}

type AuthMode = 'login' | 'register';

const LoginRegister: React.FC<LoginRegisterProps> = ({ onLogin, onError }) => {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('student');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateEmail(email)) {
      onError('Por favor, introduce un email válido');
      return;
    }

    if (mode === 'register' && !name.trim()) {
      onError('Por favor, introduce tu nombre');
      return;
    }

    setIsLoading(true);
    onError(''); // Clear previous errors

    try {
      const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api';
      
      if (mode === 'login') {
        // Login request
        const response = await fetch(`${API_BASE_URL}/user/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email }),
        });

        const data = await response.json();

        if (data.success) {
          onLogin(email, data.name, data.user_id, data.role);
        } else {
          onError(data.message || 'Error al iniciar sesión. Verifica tu email.');
        }
      } else {
        // Register request
        const response = await fetch(`${API_BASE_URL}/user/create`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, name, role }),
        });

        const data = await response.json();

        if (data.success) {
          // After successful registration, automatically log in
          onLogin(email, name, data.user_id, role);
        } else {
          onError(data.message || 'Error al crear la cuenta.');
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      onError('Error de conexión. Por favor, inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-register-container">
      <div className="login-register-box">
        <div className="login-register-header">
          <h1>Chatbot UGR</h1>
          <p>CEPRUD - Centro de Estudios de Postgrado</p>
        </div>

        <div className="auth-mode-toggle">
          <button
            className={mode === 'login' ? 'active' : ''}
            onClick={() => setMode('login')}
            disabled={isLoading}
          >
            Iniciar Sesión
          </button>
          <button
            className={mode === 'register' ? 'active' : ''}
            onClick={() => setMode('register')}
            disabled={isLoading}
          >
            Registrarse
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="name">Nombre completo</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tu nombre completo"
                required
                disabled={isLoading}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu.email@correo.ugr.es"
              required
              disabled={isLoading}
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="role">Tipo de usuario</label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                disabled={isLoading}
              >
                <option value="student">Estudiante</option>
                <option value="teacher">Profesor</option>
              </select>
            </div>
          )}

          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading 
              ? 'Procesando...' 
              : mode === 'login' 
                ? 'Iniciar Sesión' 
                : 'Crear Cuenta'
            }
          </button>
        </form>

        {mode === 'login' ? (
          <p className="auth-footer">
            ¿No tienes cuenta?{' '}
            <button 
              className="link-button" 
              onClick={() => setMode('register')}
              disabled={isLoading}
            >
              Regístrate aquí
            </button>
          </p>
        ) : (
          <p className="auth-footer">
            ¿Ya tienes cuenta?{' '}
            <button 
              className="link-button" 
              onClick={() => setMode('login')}
              disabled={isLoading}
            >
              Inicia sesión aquí
            </button>
          </p>
        )}
      </div>
    </div>
  );
};

export default LoginRegister;
