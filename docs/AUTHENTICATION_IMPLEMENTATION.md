# User Authentication System Implementation

## Overview
This document describes the implementation of a complete user authentication system for the Chatbot UGR application, replacing the simple email input with a proper login/register flow.

## Changes Made

### 1. Frontend Components

#### New Components Created

##### `LoginRegister.tsx` and `LoginRegister.css`
- **Location**: `frontend/src/components/`
- **Purpose**: Main authentication UI component
- **Features**:
  - Toggle between login and register modes
  - Form validation for email and name
  - Role selection (student/teacher) during registration
  - Loading states during API calls
  - Error handling and display
  - Responsive design with modern UI

##### `AuthContext.tsx`
- **Location**: `frontend/src/contexts/`
- **Purpose**: Global authentication state management
- **Features**:
  - React Context for sharing auth state across the app
  - Persistent authentication using localStorage
  - Login/logout functionality
  - User data management (userId, email, name, role)
  - Automatic session restoration on page reload

#### Modified Components

##### `App.tsx`
- Added `useAuth` hook integration
- Conditional rendering: shows `LoginRegister` if user is not authenticated
- Passes authenticated user to child components
- Handles login/logout workflows
- Removed email validation requirement from chat input
- Added auth error overlay for displaying authentication errors

##### `SettingsPanel.tsx`
- **Before**: Had email input field for manual entry
- **After**: Shows read-only user information (name, email, role)
- Added logout button
- Displays role in Spanish (Estudiante, Profesor, Administrador)
- Cleaner, card-based layout for user info

##### `main.tsx`
- Wrapped the app with `AuthProvider` to enable global authentication state
- Provider hierarchy: `AuthProvider` → `SessionProvider` → `App`

### 2. Frontend State Management

#### `types.ts`
- Added `AuthUser` interface with properties:
  - `userId`: Unique user identifier
  - `email`: User's email address
  - `name`: User's full name
  - `role`: User role (student, teacher, admin)
  - `isAuthenticated`: Authentication status flag

#### `api.ts`
- Added authentication API methods:
  - `login(email)`: Authenticate existing user
  - `register(email, name, role)`: Create new user account
  - `logout()`: End user session
- These methods interface with the existing backend endpoints

#### `useSessionManagement.ts`
- Updated to accept `userEmail` as a prop
- Automatically syncs with authenticated user's email
- Removed manual user settings persistence (now handled by AuthContext)
- Maintains backward compatibility with LTI mode

### 3. Styling

#### `App.css`
- Added `.user-info` and related styles for the new settings panel layout
- Added `.logout-button` with danger color scheme
- Added `.auth-error-overlay` and `.auth-error-message` for error notifications
- Smooth animations for error messages (slideDown animation)
- Responsive design considerations

#### `LoginRegister.css`
- Modern gradient background for auth screen
- Card-based layout with shadow effects
- Toggle buttons for switching between login/register
- Smooth transitions and hover effects
- Mobile-responsive design
- Accessibility-friendly form inputs

## Backend Integration

### Existing Endpoints Used
The implementation uses the existing backend user management endpoints:

1. **POST /user/create**
   - Creates a new user account
   - Body: `{ email, name, role }`
   - Returns: `{ success, user_id, message }`

2. **POST /user/login**
   - Authenticates a user by email
   - Body: `{ email }`
   - Returns: `{ success, user_id, name, role, message }`

3. **POST /user/logout**
   - Logs out the current user
   - Returns: `{ success, message }`

These endpoints were already implemented in:
- `app/routes/users.py`
- `app/core/models.py` (Pydantic models)

## User Flow

### Registration Flow
1. User opens the app (not authenticated)
2. `LoginRegister` component is displayed
3. User clicks "Registrarse" tab
4. User fills in: name, email, and role
5. On submit, calls `POST /user/create`
6. If successful, automatically logs in the user
7. User is redirected to the main chat interface

### Login Flow
1. User opens the app (not authenticated)
2. `LoginRegister` component is displayed (default: login mode)
3. User enters their email
4. On submit, calls `POST /user/login`
5. If successful, user data is stored in AuthContext and localStorage
6. User is redirected to the main chat interface

### Logout Flow
1. Authenticated user clicks "Cerrar Sesión" in settings panel
2. AuthContext clears user data
3. localStorage is cleared (auth + sessions)
4. User is redirected to login screen

## Data Persistence

### Authentication Data
- **Storage**: `localStorage` with key `chatbot_auth_user`
- **Format**: JSON object with user data
- **Lifecycle**: Persists across page reloads, cleared on logout

### Session Data
- Chat sessions remain tied to user email
- Sessions are cleared when user logs out
- Old sessions are automatically cleaned (24-hour retention)

## Security Considerations

1. **Client-Side Only**: This is a simple email-based auth (no passwords)
2. **Trust Model**: Assumes users will use their actual UGR email
3. **Session Storage**: Uses localStorage (accessible via JavaScript)
4. **No Password**: Suitable for internal/trusted environments
5. **Future Enhancement**: Could add OAuth2 or UGR SSO integration

## Testing Checklist

- [ ] User can register a new account
- [ ] User can login with existing email
- [ ] User data persists after page reload
- [ ] User can logout successfully
- [ ] Chat sessions work with authenticated user
- [ ] Subject management works with authenticated user
- [ ] LTI mode still works (bypasses auth screen)
- [ ] Error messages display correctly
- [ ] Responsive design works on mobile
- [ ] Browser back button doesn't break auth flow

## Migration Notes

### For Existing Users
- Old sessions stored with manual email entry will still work
- Users will need to register/login the first time
- No data migration needed (sessions are temporary)

### For Developers
- The email input in SettingsPanel is completely removed
- All components should use `useAuth()` instead of direct email input
- AuthContext provides a single source of truth for user data

## Future Enhancements

1. **Password Protection**: Add password-based authentication
2. **UGR SSO Integration**: Use university single sign-on
3. **Profile Editing**: Allow users to update their name/role
4. **Admin Panel**: Manage users and view analytics
5. **Remember Me**: Optional persistent login beyond session
6. **Email Verification**: Verify @correo.ugr.es domain
7. **Session Timeout**: Auto-logout after inactivity

## Files Modified/Created

### Created
- `frontend/src/components/LoginRegister.tsx`
- `frontend/src/components/LoginRegister.css`
- `frontend/src/contexts/AuthContext.tsx`

### Modified
- `frontend/src/App.tsx`
- `frontend/src/components/SettingsPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/types.ts`
- `frontend/src/api.ts`
- `frontend/src/hooks/useSessionManagement.ts`
- `frontend/src/App.css`

### Backend (No Changes)
- All necessary endpoints already existed
- No backend modifications required

## Summary

This implementation provides a complete, user-friendly authentication system that:
- ✅ Removes the confusing email input field
- ✅ Provides clear login/register interface
- ✅ Maintains user session across page reloads
- ✅ Integrates seamlessly with existing backend
- ✅ Maintains LTI compatibility
- ✅ Follows React best practices
- ✅ Includes proper error handling
- ✅ Features responsive, modern UI design
