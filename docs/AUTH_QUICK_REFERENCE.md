---
layout: default
title: Referencia Rápida de Autenticación
nav_order: 11
parent: Documentación
permalink: /docs/auth-quick-reference
---

# Authentication System - Quick Reference
{: .no_toc }

## Tabla de Contenidos
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Before vs After

### Before 🔴
```
User opens app → Sees chat + email input → Must manually enter email → Can chat
```
**Problems:**
- Confusing UX (email input only useful for registered users)
- No way to register
- No persistent user identity
- Had to remember to enter email each time

### After ✅
```
User opens app → Login/Register screen → Authenticates → Can chat
```
**Benefits:**
- Clear registration flow
- Persistent login (remembers user)
- Professional authentication UI
- User profile display
- Logout functionality

## Visual Changes

### Settings Panel (Sidebar)

**Before:**
```
┌─────────────────────────────┐
│ Configuración               │
│                             │
│ Email UGR                   │
│ [_____________________]     │
│ Email inválido              │
│ Tu email se usa para...     │
└─────────────────────────────┘
```

**After:**
```
┌─────────────────────────────┐
│ Mi Cuenta                   │
│                             │
│ Nombre                      │
│ Juan Pérez                  │
│                             │
│ Email                       │
│ juan.perez@correo.ugr.es   │
│                             │
│ Rol                         │
│ Estudiante                  │
│                             │
│ [ Cerrar Sesión ]          │
└─────────────────────────────┘
```

### Initial Screen

**Before:**
```
User sees chat interface immediately
with email input at bottom of sidebar
```

**After:**
```
┌────────────────────────────────────┐
│        Chatbot UGR                 │
│  CEPRUD - Centro de Estudios...   │
│                                    │
│  [Iniciar Sesión] [Registrarse]   │
│                                    │
│  Email                             │
│  [________________________]        │
│                                    │
│  [    Iniciar Sesión     ]        │
│                                    │
│  ¿No tienes cuenta? Regístrate     │
└────────────────────────────────────┘
```

## Component Architecture

```
App (Root)
├── AuthProvider (Context)
│   └── SessionProvider (Context)
│       └── App Component
│           ├── LoginRegister (if not authenticated)
│           │   ├── Login Form
│           │   └── Register Form
│           │
│           └── Main Interface (if authenticated)
│               ├── Sidebar
│               │   ├── SubjectList
│               │   └── SettingsPanel (user info + logout)
│               │
│               └── Chat Area
│                   ├── Messages
│                   └── Input
```

## API Endpoints Used

### Registration
```http
POST /user/create
Content-Type: application/json

{
  "email": "user@correo.ugr.es",
  "name": "Juan Pérez",
  "role": "student"
}

Response:
{
  "success": true,
  "user_id": "abc123",
  "message": "User created successfully"
}
```

### Login
```http
POST /user/login
Content-Type: application/json

{
  "email": "user@correo.ugr.es"
}

Response:
{
  "success": true,
  "user_id": "abc123",
  "name": "Juan Pérez",
  "role": "student",
  "message": "Login successful"
}
```

### Logout
```http
POST /user/logout

Response:
{
  "success": true,
  "message": "Logout successful"
}
```

## Storage Structure

### localStorage Keys

```javascript
// Before
localStorage = {
  'chatbot_user_email': 'user@correo.ugr.es',
  'chatbot_sessions': '[...]',
  'chatbot_selected_subject': 'subject_id'
}

// After
localStorage = {
  'chatbot_auth_user': '{userId, email, name, role, isAuthenticated}',
  'chatbot_sessions': '[...]',
  'chatbot_selected_subject': 'subject_id'
  // Note: chatbot_user_email is no longer used
}
```

## Code Examples

### Using Authentication in Components

```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, logout, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return (
    <div>
      <p>Welcome, {user.name}!</p>
      <p>Email: {user.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Handling Login/Register

```typescript
const handleLogin = (email, name, userId, role) => {
  login(email, name, userId, role); // From AuthContext
  // User is now authenticated and redirected
};

const handleError = (message) => {
  setAuthError(message); // Display error to user
};
```

## Testing Commands

```bash
# Start the frontend development server
cd frontend
npm run dev

# The app will be available at http://localhost:3000

# Test registration:
# 1. Click "Registrarse"
# 2. Fill in: name, email, role
# 3. Click "Crear Cuenta"
# 4. Should redirect to chat interface

# Test login:
# 1. Logout if logged in
# 2. Click "Iniciar Sesión"
# 3. Enter registered email
# 4. Click "Iniciar Sesión"
# 5. Should redirect to chat interface

# Test persistence:
# 1. Login
# 2. Refresh page
# 3. Should remain logged in

# Test logout:
# 1. Click "Cerrar Sesión" in sidebar
# 2. Should redirect to login screen
# 3. All sessions should be cleared
```

## Common Issues & Solutions

### Issue: "User not found" when logging in
**Solution:** Make sure the user is registered first. Click "Registrarse" to create an account.

### Issue: Login screen doesn't appear after logout
**Solution:** Clear browser localStorage and refresh the page.

### Issue: Email validation error
**Solution:** Use a valid email format (e.g., user@correo.ugr.es).

### Issue: Authentication state not persisting
**Solution:** Check browser console for localStorage errors. Ensure localStorage is enabled.

### Issue: Backend connection error
**Solution:** Verify backend is running on port 8080 and CORS is configured correctly.

## Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ⚠️ IE11 (not supported - uses modern React features)

## Mobile Responsive

The login/register form is fully responsive:
- Desktop: Centered card with gradient background
- Tablet: Slightly narrower card
- Mobile: Full-width with padding, optimized form fields
