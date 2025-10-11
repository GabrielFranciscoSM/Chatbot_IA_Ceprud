# Component Architecture Diagram

## Authentication Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          main.tsx                               │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      AuthProvider                          │ │
│  │                    (Global Auth State)                     │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                  SessionProvider                      │ │ │
│  │  │                  (LTI Integration)                    │ │ │
│  │  │  ┌────────────────────────────────────────────────┐  │ │ │
│  │  │  │                 App.tsx                        │  │ │ │
│  │  │  │                                                │  │ │ │
│  │  │  │  ┌──────────────────────────────────────────┐ │  │ │ │
│  │  │  │  │  isAuthenticated? Check                  │ │  │ │ │
│  │  │  │  └─────────────┬────────────────────────────┘ │  │ │ │
│  │  │  │                │                              │  │ │ │
│  │  │  │        ┌───────┴────────┐                    │  │ │ │
│  │  │  │        │                │                    │  │ │ │
│  │  │  │       NO               YES                   │  │ │ │
│  │  │  │        │                │                    │  │ │ │
│  │  │  │        ▼                ▼                    │  │ │ │
│  │  │  │  ┌──────────┐    ┌────────────────────┐     │  │ │ │
│  │  │  │  │  Login/  │    │  Main Chat App     │     │  │ │ │
│  │  │  │  │ Register │    │                    │     │  │ │ │
│  │  │  │  │  Screen  │    │  ┌──────────────┐  │     │  │ │ │
│  │  │  │  │          │    │  │   Sidebar    │  │     │  │ │ │
│  │  │  │  └──────────┘    │  │              │  │     │  │ │ │
│  │  │  │                  │  │ ┌──────────┐ │  │     │  │ │ │
│  │  │  │                  │  │ │ Subject  │ │  │     │  │ │ │
│  │  │  │                  │  │ │  List    │ │  │     │  │ │ │
│  │  │  │                  │  │ └──────────┘ │  │     │  │ │ │
│  │  │  │                  │  │              │  │     │  │ │ │
│  │  │  │                  │  │ ┌──────────┐ │  │     │  │ │ │
│  │  │  │                  │  │ │ Settings │ │  │     │  │ │ │
│  │  │  │                  │  │ │  Panel   │ │  │     │  │ │ │
│  │  │  │                  │  │ │(Profile) │ │  │     │  │ │ │
│  │  │  │                  │  │ └──────────┘ │  │     │  │ │ │
│  │  │  │                  │  └──────────────┘  │     │  │ │ │
│  │  │  │                  │                    │     │  │ │ │
│  │  │  │                  │  ┌──────────────┐  │     │  │ │ │
│  │  │  │                  │  │  Chat Area   │  │     │  │ │ │
│  │  │  │                  │  │              │  │     │  │ │ │
│  │  │  │                  │  │  Messages    │  │     │  │ │ │
│  │  │  │                  │  │  Input       │  │     │  │ │ │
│  │  │  │                  │  └──────────────┘  │     │  │ │ │
│  │  │  │                  └────────────────────┘     │  │ │ │
│  │  │  └────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## State Management Flow

```
┌──────────────────────────────────────────────────────────────┐
│                        AuthContext                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  State:                                                │  │
│  │    - user: AuthUser | null                            │  │
│  │    - isAuthenticated: boolean                         │  │
│  │                                                        │  │
│  │  Methods:                                             │  │
│  │    - login(email, name, userId, role)                 │  │
│  │    - logout()                                         │  │
│  │                                                        │  │
│  │  Storage:                                             │  │
│  │    - localStorage['chatbot_auth_user']               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │             Available to all components via:           │  │
│  │                  useAuth() hook                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                                │
                                │ user.email
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                   useSessionManagement                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  - Receives user email as prop                        │  │
│  │  - Creates/manages chat sessions                      │  │
│  │  - Persists to localStorage                           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Authentication Sequence Diagram

### Registration Flow
```
User                LoginRegister           API                 AuthContext
 │                       │                   │                       │
 │  Fill form           │                   │                       │
 │  Click "Crear        │                   │                       │
 │  Cuenta"             │                   │                       │
 ├──────────────────────>│                   │                       │
 │                       │  POST            │                       │
 │                       │  /user/create    │                       │
 │                       ├──────────────────>│                       │
 │                       │                   │                       │
 │                       │  {success: true,  │                       │
 │                       │   user_id, ...}   │                       │
 │                       │<──────────────────┤                       │
 │                       │                   │                       │
 │                       │  login(email,     │                       │
 │                       │   name, userId,   │                       │
 │                       │   role)           │                       │
 │                       ├───────────────────────────────────────────>│
 │                       │                   │                       │
 │                       │                   │  Store in            │
 │                       │                   │  localStorage        │
 │                       │                   │  Set user state      │
 │                       │                   │<──────────────────────┤
 │                       │                   │                       │
 │  Redirect to          │                   │                       │
 │  chat interface       │                   │                       │
 │<──────────────────────┤                   │                       │
 │                       │                   │                       │
```

### Login Flow
```
User                LoginRegister           API                 AuthContext
 │                       │                   │                       │
 │  Enter email         │                   │                       │
 │  Click "Iniciar      │                   │                       │
 │  Sesión"             │                   │                       │
 ├──────────────────────>│                   │                       │
 │                       │  POST            │                       │
 │                       │  /user/login     │                       │
 │                       ├──────────────────>│                       │
 │                       │                   │                       │
 │                       │  {success: true,  │                       │
 │                       │   user_id,        │                       │
 │                       │   name, role}     │                       │
 │                       │<──────────────────┤                       │
 │                       │                   │                       │
 │                       │  login(...)       │                       │
 │                       ├───────────────────────────────────────────>│
 │                       │                   │                       │
 │                       │                   │  Store in            │
 │                       │                   │  localStorage        │
 │                       │                   │  Set user state      │
 │                       │                   │<──────────────────────┤
 │                       │                   │                       │
 │  Redirect to          │                   │                       │
 │  chat interface       │                   │                       │
 │<──────────────────────┤                   │                       │
 │                       │                   │                       │
```

### Logout Flow
```
User            SettingsPanel        AuthContext         localStorage
 │                    │                    │                   │
 │  Click "Cerrar    │                    │                   │
 │  Sesión"          │                    │                   │
 ├───────────────────>│                    │                   │
 │                    │  logout()         │                   │
 │                    ├───────────────────>│                   │
 │                    │                    │  Clear all       │
 │                    │                    │  auth data       │
 │                    │                    ├──────────────────>│
 │                    │                    │                   │
 │                    │                    │  Clear sessions  │
 │                    │                    ├──────────────────>│
 │                    │                    │                   │
 │                    │  Set user = null  │                   │
 │                    │<───────────────────┤                   │
 │                    │                    │                   │
 │  Redirect to       │                    │                   │
 │  login screen      │                    │                   │
 │<───────────────────┤                    │                   │
 │                    │                    │                   │
```

## Component Dependency Tree

```
App.tsx
├── useAuth()                    ← From AuthContext
├── useSession()                 ← From SessionContext (LTI)
├── useSessionManagement()       ← Custom hook
│   ├── loadSessionsFromStorage()
│   ├── saveSessionsToStorage()
│   └── findOrCreateSession()
├── useSubjectManagement()       ← Custom hook
└── useChatHandling()           ← Custom hook

AuthContext.tsx
├── useState(user)
├── localStorage operations
└── Provides useAuth() hook

LoginRegister.tsx
├── useState(mode, email, name, role)
├── API calls (POST /user/create, /user/login)
├── Form validation
└── Calls onLogin callback → AuthContext.login()

SettingsPanel.tsx
├── useAuth() hook
├── Display user info
└── Logout button → AuthContext.logout()
```

## Data Flow Diagram

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌──────────────────┐     ┌─────────────┐
│ LoginRegister    │────>│     API     │
│ Component        │<────│  /user/*    │
└────────┬─────────┘     └─────────────┘
         │
         │ onLogin()
         ▼
┌──────────────────┐     ┌──────────────┐
│   AuthContext    │────>│ localStorage │
│   login()        │<────│              │
└────────┬─────────┘     └──────────────┘
         │
         │ user state updated
         ▼
┌──────────────────┐
│    App.tsx       │
│  Re-renders      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────┐
│  isAuthenticated │────>│   Render     │
│      check       │     │ Chat Interface│
└──────────────────┘     └──────────────┘
```

## File Structure Overview

```
frontend/src/
│
├── main.tsx                          ← Entry point, wraps with providers
│
├── App.tsx                           ← Main app logic, auth routing
│
├── contexts/
│   ├── AuthContext.tsx              ← NEW: Auth state management
│   └── SessionContext.tsx           ← Existing: LTI integration
│
├── components/
│   ├── LoginRegister.tsx            ← NEW: Auth UI
│   ├── LoginRegister.css            ← NEW: Auth styling
│   ├── SettingsPanel.tsx            ← MODIFIED: Shows profile now
│   ├── SubjectSidebar.tsx           ← Unchanged
│   ├── ChatInput.tsx                ← Unchanged
│   └── ... (other components)
│
├── hooks/
│   ├── useSessionManagement.ts      ← MODIFIED: Accepts userEmail prop
│   ├── useSubjectManagement.ts      ← Unchanged
│   ├── useChatHandling.ts           ← Unchanged
│   └── useSession.ts                ← Unchanged
│
├── types.ts                          ← MODIFIED: Added AuthUser type
├── api.ts                            ← MODIFIED: Added auth endpoints
├── utils.ts                          ← Mostly unchanged
├── constants.ts                      ← Unchanged
└── App.css                           ← MODIFIED: Added auth styles
```

## Key Interactions

### 1. App Initialization
```
Page Load
    ↓
AuthContext loads from localStorage
    ↓
Is user data valid?
    ├─ YES → Set isAuthenticated = true
    │        ↓
    │        App renders chat interface
    │
    └─ NO  → Set isAuthenticated = false
             ↓
             App renders LoginRegister
```

### 2. After Login Success
```
API returns user data
    ↓
AuthContext.login() called
    ↓
User data saved to localStorage
    ↓
User state updated
    ↓
App re-renders
    ↓
isAuthenticated = true
    ↓
Chat interface displayed
```

### 3. Logout Process
```
User clicks "Cerrar Sesión"
    ↓
AuthContext.logout() called
    ↓
Clear localStorage (auth + sessions)
    ↓
Set user = null
    ↓
App re-renders
    ↓
isAuthenticated = false
    ↓
LoginRegister displayed
```
