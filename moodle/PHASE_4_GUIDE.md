# Phase 3 → Phase 4 Transition Guide

## ✅ Phase 3 Complete!

All backend LTI integration is done. The chatbot can now:
- Accept LTI launches from Moodle
- Validate JWT tokens
- Create/manage users from LTI
- Create sessions with secure tokens
- Map courses to subjects
- Redirect to the chat UI

## 🚀 What's Next: Phase 4 - Frontend Integration

### Goal
Update the React frontend to support LTI mode with session-based authentication.

### Changes Needed

#### 1. URL Parameter Handling
The frontend receives:
```
http://localhost:5173/?session_token=ABC123&lti=true&subject=Matematicas
```

Need to:
- Parse `session_token` from URL
- Detect `lti=true` mode
- Extract `subject` parameter
- Store session token for API calls

#### 2. Session Authentication
Currently: Frontend may use JWT tokens or other auth
Needed: Use session token for LTI users

**Files to modify**:
- `frontend/src/main.tsx` or `frontend/src/App.tsx` (URL parsing)
- API client/service files (add session token to requests)

#### 3. LTI Mode UI Adjustments
When `lti=true`:
- Hide navigation (user can't leave iframe)
- Hide login/signup (already authenticated)
- Display course/subject context
- Optimize for iframe embedding
- Responsive design for various iframe sizes

#### 4. API Request Updates
All API calls need to include session token:
```typescript
headers: {
  'X-Session-Token': sessionToken,
  // or
  'Authorization': `Bearer ${sessionToken}`
}
```

### Implementation Steps

#### Step 1: Parse URL Parameters
```typescript
// In App.tsx or a utility file
const params = new URLSearchParams(window.location.search);
const sessionToken = params.get('session_token');
const isLTI = params.get('lti') === 'true';
const subject = params.get('subject');

if (sessionToken) {
  // Store in state/context
  localStorage.setItem('session_token', sessionToken);
}
```

#### Step 2: Create Session Context
```typescript
// src/contexts/SessionContext.tsx
interface SessionContextType {
  sessionToken: string | null;
  isLTI: boolean;
  subject: string | null;
  user: User | null;
}

export const SessionProvider = ({ children }) => {
  const [session, setSession] = useState<SessionContextType>({
    sessionToken: localStorage.getItem('session_token'),
    isLTI: false,
    subject: null,
    user: null
  });
  
  // Load user from session token
  useEffect(() => {
    if (session.sessionToken) {
      fetchUserFromSession(session.sessionToken);
    }
  }, [session.sessionToken]);
  
  return (
    <SessionContext.Provider value={session}>
      {children}
    </SessionContext.Provider>
  );
};
```

#### Step 3: Update API Client
```typescript
// src/services/api.ts
const getHeaders = () => {
  const sessionToken = localStorage.getItem('session_token');
  return {
    'Content-Type': 'application/json',
    ...(sessionToken && { 'X-Session-Token': sessionToken })
  };
};

export const apiClient = {
  get: (url) => fetch(url, { headers: getHeaders() }),
  post: (url, data) => fetch(url, { 
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data)
  }),
  // ...
};
```

#### Step 4: Backend Session Validation
Add endpoint to validate session and get user:
```python
# app/api_router.py
@router.get("/api/session/validate")
async def validate_session(session_token: str = Header(None, alias="X-Session-Token")):
    if not session_token:
        raise HTTPException(401, "No session token")
    
    session = await lti_session_service.get_session(session_token)
    if not session:
        raise HTTPException(401, "Invalid session")
    
    user = await user_service.get_user_by_id(session["user_id"])
    return {
        "user": user,
        "subject": session["subject"],
        "context_label": session["context_label"]
    }
```

#### Step 5: Conditional UI Rendering
```typescript
// src/App.tsx
const App = () => {
  const { isLTI, subject } = useSession();
  
  return (
    <div className={isLTI ? 'lti-mode' : 'standalone-mode'}>
      {!isLTI && <Header />}
      {!isLTI && <Navigation />}
      
      {isLTI && subject && (
        <div className="context-banner">
          📚 {subject}
        </div>
      )}
      
      <ChatInterface />
      
      {!isLTI && <Footer />}
    </div>
  );
};
```

#### Step 6: LTI CSS Adjustments
```css
/* src/styles/lti.css */
.lti-mode {
  height: 100vh;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.lti-mode .header,
.lti-mode .footer,
.lti-mode .navigation {
  display: none;
}

.context-banner {
  background: #f0f0f0;
  padding: 8px 16px;
  border-bottom: 1px solid #ccc;
  font-size: 14px;
}
```

### Testing Phase 4

#### Local Testing
1. Start backend with LTI support
2. Start frontend
3. Navigate to: `http://localhost:5173/?session_token=TEST123&lti=true&subject=Matematicas`
4. Verify:
   - Session loaded
   - User authenticated
   - UI in LTI mode
   - Chat works

#### Moodle Testing
1. Configure LTI tool in Moodle
2. Add activity to course
3. Launch from Moodle
4. Verify iframe loads correctly
5. Test chat functionality

### Files to Create/Modify

**New Files**:
- `frontend/src/contexts/SessionContext.tsx` - Session management
- `frontend/src/hooks/useSession.ts` - Session hook
- `frontend/src/styles/lti.css` - LTI-specific styles
- `frontend/src/types/session.ts` - TypeScript types

**Modified Files**:
- `frontend/src/App.tsx` - Add session provider, conditional rendering
- `frontend/src/main.tsx` - Parse URL parameters
- `frontend/src/services/api.ts` - Add session token to requests
- `app/api_router.py` - Add session validation endpoint

### Backend Changes (if needed)

May need to add session validation middleware:
```python
# app/core/middleware.py
async def session_auth_middleware(request: Request, call_next):
    session_token = request.headers.get("X-Session-Token")
    if session_token:
        session = await lti_session_service.get_session(session_token)
        if session:
            request.state.user_id = session["user_id"]
            request.state.subject = session["subject"]
    
    response = await call_next(request)
    return response
```

### Estimated Time
- Step 1-2 (URL parsing, context): 30 min
- Step 3 (API client): 30 min
- Step 4 (Backend endpoint): 30 min
- Step 5-6 (UI/CSS): 1 hour
- Testing: 1 hour
**Total**: 3-4 hours

### Ready to Start?

Run this command to proceed to Phase 4:
```bash
echo "Phase 4: Frontend Integration"
```

Then start working on the frontend files listed above.

### Questions to Consider

1. Should session tokens be in header or as Bearer tokens?
2. How long should frontend cache the session?
3. What happens when session expires?
4. Should we show a logout button in LTI mode?
5. How to handle multiple concurrent Moodle courses?

### Success Criteria

✅ Frontend parses session_token from URL
✅ Frontend validates session with backend
✅ User auto-logged in from LTI session
✅ UI adapts to LTI mode (no nav, optimized for iframe)
✅ Subject context displayed
✅ Chat works with session authentication
✅ Works in Moodle iframe

---

**Current Status**: Ready for Phase 4
**Next Action**: Modify frontend to handle LTI sessions
