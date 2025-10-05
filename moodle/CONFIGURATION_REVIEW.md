# 🔍 Project Configuration Review - Chatbot IA CEPRUD

**Date**: October 5, 2025  
**Branch**: `feature/moodle_integration`  
**Review Focus**: LTI 1.3 Integration & System Configuration

---

## 📊 Executive Summary

### ✅ What's Working
- **Phase 3 Backend LTI**: 100% complete (27/27 tests passing)
- **Microservices Architecture**: Fully implemented with Docker Compose
- **User Management**: MongoDB integration working
- **RAG Service**: ChromaDB with embeddings functional
- **Frontend**: React/TypeScript with Vite, proxy configured

### 🚧 What Needs Work
- **Phase 4 Frontend LTI**: Not implemented yet
- **vLLM Services**: Commented out in docker-compose (infrastructure tests failing)
- **Monitoring Stack**: Prometheus/Grafana not running
- **LTI Frontend Integration**: Session token handling missing

---

## 🏗️ System Architecture Overview

### Current Stack

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
│  React + TypeScript + Vite → Nginx (Port 8090)         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   API GATEWAY                            │
│  FastAPI Backend (Port 8080)                            │
│  - REST API (/chat, /user/*, /health)                  │
│  - LTI Routes (/lti/jwks, /lti/login, /lti/launch)    │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐      ┌──────────────────────────┐
│  RAG SERVICE     │      │  USER SERVICE            │
│  Port 8082       │      │  Port 8083               │
│  - ChromaDB      │      │  - MongoDB API           │
│  - Embeddings    │      │  - User CRUD             │
└──────────────────┘      └──────────┬───────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │  MongoDB             │
                          │  Port 27017          │
                          │  - User Data         │
                          │  - LTI Sessions      │
                          └──────────────────────┘
```

---

## 🔐 LTI 1.3 Configuration Status

### ✅ Backend Implementation (COMPLETE)

**Files Implemented:**
- `app/lti/__init__.py` - Module initialization
- `app/lti/config.py` - RSA key management, JWKS generation
- `app/lti/models.py` - Pydantic models for LTI data
- `app/lti/routes.py` - LTI endpoints (JWKS, login, launch)
- `app/lti/jwt_validator.py` - JWT signature validation
- `app/lti/user_service.py` - User creation from LTI claims
- `app/lti/session_service.py` - Session management with MongoDB
- `app/lti/database.py` - Motor async MongoDB connection

**Endpoints Available:**
```
GET  /lti/jwks         → Public keyset for Moodle
GET  /lti/login        → OIDC login initiation
POST /lti/launch       → LTI launch handler (validates JWT, creates session)
```

**Configuration Files:**
- `lti_config/private_key.pem` ✅ Generated (1704 bytes)
- `lti_config/public_key.pem` ✅ Generated (451 bytes)
- `lti_config/jwks.json` ✅ Generated (kid: lti-key-1)
- `moodle/.env` ✅ Configured for testchatbot.moodlecloud.com

**Moodle Platform Configuration:**
```properties
MOODLE_PLATFORM_ID="https://testchatbot.moodlecloud.com"
MOODLE_CLIENT_ID="GBx1F4LefiUr7bZ"
MOODLE_AUTH_LOGIN_URL="https://testchatbot.moodlecloud.com/mod/lti/auth.php"
MOODLE_AUTH_TOKEN_URL="https://testchatbot.moodlecloud.com/mod/lti/token.php"
MOODLE_KEY_SET_URL="https://testchatbot.moodlecloud.com/mod/lti/certs.php"
MOODLE_DEPLOYMENT_ID="1"
CHATBOT_BASE_URL="http://150.214.22.87:8080"
```

**Course Mapping (Hard-coded):**
```python
COURSE_SUBJECT_MAPPING = {
    "ASIG001": "Matematicas",
    "ASIG002": "Fisica",
}
```

### 🚧 Frontend Implementation (PENDING)

**Current Frontend Setup:**
- React 18.2.0 with TypeScript
- Vite 5.4.0 for development
- Axios for API calls
- No LTI session handling yet

**What's Missing:**
1. ❌ URL parameter parsing for `session_token`, `lti`, `subject`
2. ❌ Session context provider
3. ❌ API client session token headers
4. ❌ LTI mode UI (hide navigation, optimize for iframe)
5. ❌ Backend session validation endpoint

**Files That Need Creation:**
- `frontend/src/contexts/SessionContext.tsx` - Session management
- `frontend/src/hooks/useSession.ts` - Session hook
- `frontend/src/styles/lti.css` - LTI-specific styles
- `frontend/src/types/session.ts` - TypeScript types

**Files That Need Modification:**
- `frontend/src/App.tsx` - Add session provider, conditional rendering
- `frontend/src/main.tsx` - Parse URL parameters
- `frontend/src/api.ts` - Add session token to requests
- `app/api_router.py` - Add `/api/session/validate` endpoint

---

## 🐳 Docker Configuration

### Services Defined in `docker-compose-full.yml`

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| **mongodb** | ✅ Running | 27017 | User data, LTI sessions |
| **mongo-express** | ✅ Running | 8081 | DB admin interface |
| **user-service** | ✅ Running | 8083 | MongoDB API wrapper |
| **rag-service** | ✅ Running | 8082 | ChromaDB + embeddings |
| **logging-service** | ✅ Running | 8002 | Analytics & logs |
| **backend** | ✅ Running | 8080 | FastAPI + LTI routes |
| **frontend** | ✅ Running | 8090 | Nginx serving React build |
| **vllm-openai** | ❌ Commented | 8000 | LLM inference (GPU required) |
| **vllm-openai-embeddings** | ❌ Commented | 8001 | Embedding generation (GPU) |

### Why vLLM Services Are Commented Out
- Require NVIDIA GPU (device_ids: ['0'])
- Using external vLLM endpoints or alternative for now
- Tests failing because containers don't exist (expected)

### Network Configuration
```yaml
networks:
  default:
    name: chatbot-network
```

All services on same Docker network for inter-service communication.

---

## 📦 Dependencies

### Backend (`requirements.txt`)
**Key LTI Dependencies:**
```
PyLTI1p3==2.0.0          # LTI 1.3 framework
PyJWT==2.10.1            # JWT token handling
cryptography==46.0.2     # RSA key operations
jwcrypto==1.5.6          # JWK/JWKS handling
motor==3.6.0             # Async MongoDB driver
```

**Other Critical Dependencies:**
- FastAPI 0.116.1 + Uvicorn 0.35.0
- LangChain 0.3.26 (RAG orchestration)
- Transformers 4.53.3 (HuggingFace)
- ChromaDB (via langchain dependencies)
- Pandas, Matplotlib, Seaborn (analytics)

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "axios": "^1.7.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^10.1.0",
    "lucide-react": "^0.400.0",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "vite": "^5.4.0",
    "typescript": "^5.2.2",
    "@vitejs/plugin-react": "^4.2.1"
  }
}
```

---

## 🔌 API Endpoints

### Core Chat API
```
POST /chat                    → Send message, get response
POST /clear-session          → Clear conversation memory
GET  /health                 → Health check
GET  /rate-limit/{email}     → Check rate limit status
```

### User Management API
```
POST /user/create            → Create new user
POST /user/login             → Login user (email-based)
POST /user/logout            → Logout user
GET  /user/profile?email=    → Get user profile
PUT  /user/profile?email=    → Update user profile
```

### Subject Management API
```
GET    /user/subjects?email=          → Get user's subjects
POST   /user/subjects                 → Add subject to user
DELETE /user/subjects/{id}?email=     → Remove subject from user
```

### LTI API
```
GET  /lti/jwks               → Public keyset (JWKS)
GET  /lti/login              → OIDC login initiation
POST /lti/launch             → LTI launch handler
```

### Missing (Needed for Phase 4)
```
GET  /api/session/validate   → Validate LTI session token
```

---

## 🔄 Current Data Flow

### Standard Chat Flow (Without LTI)
```
1. User types message in React frontend
2. Frontend sends POST /chat with { message, subject, email, mode }
3. Backend validates rate limit (20 req/min)
4. Backend calls RAG service for context
5. RAG service queries ChromaDB for relevant documents
6. Backend generates response (using LLM or fallback)
7. Backend logs to logging service
8. Response returned to frontend with sources
```

### LTI Flow (Phase 3 - Backend Only)
```
1. Moodle user clicks LTI activity
2. Moodle redirects to GET /lti/login
3. Backend redirects to Moodle OIDC auth URL
4. Moodle authenticates user, generates JWT
5. Moodle POSTs JWT to /lti/launch
6. Backend validates JWT signature
7. Backend creates/updates user in MongoDB
8. Backend creates session with token
9. Backend redirects to frontend with session_token
10. ❌ Frontend doesn't handle session yet (Phase 4 needed)
```

---

## 🌐 Environment Variables

### Root `.env` (Backend)
```properties
MODEL_NAME="Sreenington/Phi-3-mini-4k-instruct-AWQ"
MODEL_DIR="/models/Sreenington--Phi-3-mini-4k-instruct-AWQ"
EMBEDDING_MODEL_DIR="/models/Qwen--Qwen3-Embedding-0.6B"
VLLM_URL="http://vllm-openai:8000"
VLLM_EMBEDDING_URL="http://vllm-openai-embeddings:8001"
HF_TOKEN="hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # ⚠️ REDACTED for security
GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # ⚠️ REDACTED for security
```

**⚠️ SECURITY WARNING**: API keys should NEVER be committed to Git. Use:
- `.env.example` with placeholder values (committed to Git)
- `.env` with real values (in `.gitignore`, never committed)
- Secrets management in production

### `moodle/.env` (LTI Configuration)
```properties
MOODLE_PLATFORM_ID="https://testchatbot.moodlecloud.com"
MOODLE_CLIENT_ID="GBx1F4LefiUr7bZ"
MOODLE_AUTH_LOGIN_URL="https://testchatbot.moodlecloud.com/mod/lti/auth.php"
MOODLE_AUTH_TOKEN_URL="https://testchatbot.moodlecloud.com/mod/lti/token.php"
MOODLE_KEY_SET_URL="https://testchatbot.moodlecloud.com/mod/lti/certs.php"
MOODLE_DEPLOYMENT_ID="1"
LTI_CONFIG_DIR="./lti_config"
CHATBOT_BASE_URL="http://150.214.22.87:8080"
DEFAULT_SUBJECT_MAPPINGS='{"IS": "ingenieria_de_servidores", ...}'
```

### `frontend/.env`
```properties
VITE_API_BASE_URL=/api
VITE_DEV_API_BASE_URL=http://localhost:8080
```

**Note**: Vite proxy handles `/api` → `http://backend:8080` in development.

---

## 🧪 Testing Status

### Pytest Results (Latest Run)
```
Total: 24 tests
Passed: 17 ✅
Failed: 6 ❌
Skipped: 1 ⏭️
```

**Failed Tests (Infrastructure - Expected):**
- `test_vllm_container_running` - vLLM container commented out
- `test_embeddings_container_running` - Embeddings container commented out
- `test_container_logs` - Missing containers
- `test_embeddings_service_health_endpoint` - Port 8001 not listening
- `test_prometheus_metrics` - Prometheus not running
- `test_grafana_dashboard` - Grafana not running

**Passing Tests:**
- E2E chat flow tests ✅
- API endpoint tests ✅
- Most container infrastructure tests ✅

### LTI Phase 3 Tests
```
test_phase3_review.py: 27/27 PASSED ✅
```

All LTI backend components tested and working.

---

## 🗺️ Current State vs. Required State

### For Standalone Use (No LTI)
| Component | Status | Notes |
|-----------|--------|-------|
| User registration | ✅ Working | MongoDB + API |
| User login | ✅ Working | Email-based |
| Subject selection | ✅ Working | Frontend sidebar |
| Chat interface | ✅ Working | React components |
| RAG retrieval | ✅ Working | ChromaDB |
| Message history | ✅ Working | Session-based |
| Analytics | ✅ Working | CSV logs |

**Verdict**: Standalone mode is production-ready ✅

### For Moodle LTI Integration
| Component | Status | Notes |
|-----------|--------|-------|
| LTI JWKS endpoint | ✅ Complete | `/lti/jwks` |
| LTI login redirect | ✅ Complete | `/lti/login` |
| LTI launch handler | ✅ Complete | `/lti/launch` |
| JWT validation | ✅ Complete | Signature + claims |
| User auto-creation | ✅ Complete | From LTI claims |
| Session creation | ✅ Complete | MongoDB stored |
| Course→Subject mapping | ⚠️ Hard-coded | Needs DB or config |
| Frontend session parsing | ❌ Missing | Phase 4 |
| Frontend LTI mode UI | ❌ Missing | Phase 4 |
| Session token validation API | ❌ Missing | Phase 4 |

**Verdict**: Backend ready, frontend needs Phase 4 🚧

---

## 🎯 Recommendations

### Immediate Actions (Phase 4)

#### 1. Frontend Session Context (30 min)
Create `frontend/src/contexts/SessionContext.tsx`:
```typescript
export const SessionProvider = ({ children }) => {
  const [sessionToken, setSessionToken] = useState(null);
  const [isLTI, setIsLTI] = useState(false);
  const [subject, setSubject] = useState(null);
  
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('session_token');
    const lti = params.get('lti') === 'true';
    const subj = params.get('subject');
    
    if (token) {
      setSessionToken(token);
      setIsLTI(lti);
      setSubject(subj);
      localStorage.setItem('session_token', token);
    }
  }, []);
  
  // ...
};
```

#### 2. API Client Session Headers (15 min)
Update `frontend/src/api.ts`:
```typescript
api.interceptors.request.use((config) => {
  const sessionToken = localStorage.getItem('session_token');
  if (sessionToken) {
    config.headers['X-Session-Token'] = sessionToken;
  }
  return config;
});
```

#### 3. Backend Session Validation (30 min)
Add to `app/api_router.py`:
```python
@router.get("/api/session/validate")
async def validate_session(
    session_token: str = Header(None, alias="X-Session-Token")
):
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

#### 4. Conditional UI for LTI Mode (1 hour)
Update `frontend/src/App.tsx`:
```typescript
const { isLTI, subject } = useSession();

return (
  <div className={isLTI ? 'lti-mode' : 'standalone-mode'}>
    {!isLTI && <SubjectSidebar />}
    {!isLTI && <SettingsPanel />}
    
    {isLTI && subject && (
      <div className="context-banner">📚 {subject}</div>
    )}
    
    <ChatInterface />
  </div>
);
```

### Medium-Term Improvements

#### 1. Move Course Mappings to Database
Replace hard-coded `COURSE_SUBJECT_MAPPING` with MongoDB collection:
```python
# New collection: lti_course_mappings
{
  "platform_id": "https://testchatbot.moodlecloud.com",
  "course_label": "IS",
  "subject_id": "ingenieria_de_servidores",
  "created_at": "...",
  "active": true
}
```

#### 2. Environment Variables Security
- Create `.env.example` with placeholders
- Add `.env` to `.gitignore`
- Use secrets manager for production (e.g., Docker secrets, Vault)

#### 3. Enable Monitoring Stack
Uncomment/configure in `docker-compose-full.yml`:
- Prometheus for metrics collection
- Grafana for dashboards
- Alertmanager for notifications

#### 4. LTI Session Expiration Handling
- Add automatic session refresh
- Display expiration warning in frontend
- Implement session extension endpoint

### Long-Term Enhancements

#### 1. Multi-Tenancy Support
- Support multiple Moodle instances
- Platform-specific configuration in DB
- Tenant isolation in MongoDB

#### 2. LTI Advantage Features
- Names and Roles Provisioning Service (NRPS)
- Assignment and Grading Service (AGS)
- Deep Linking 2.0

#### 3. Advanced Analytics
- Student engagement metrics per course
- Question complexity analysis
- Subject-specific performance tracking

#### 4. GPU Service Restoration
- Configure vLLM services when GPU available
- Implement model switching logic
- Load balancing for multiple GPUs

---

## 📋 Checklists

### Before Testing in Moodle

- [x] Backend LTI endpoints implemented
- [x] JWT validation working
- [x] User auto-creation functional
- [x] Session management with MongoDB
- [x] RSA keys generated
- [x] JWKS endpoint accessible
- [ ] Frontend session handling (Phase 4)
- [ ] LTI mode UI implemented (Phase 4)
- [ ] Session validation API endpoint (Phase 4)
- [ ] Testing with ngrok or public URL

### For Production Deployment

- [ ] Environment variables in secrets manager
- [ ] MongoDB authentication enabled
- [ ] HTTPS/SSL certificates configured
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting tuned for production load
- [ ] Logging to centralized service (not just files)
- [ ] Monitoring stack configured (Prometheus/Grafana)
- [ ] Backup strategy for MongoDB
- [ ] Disaster recovery plan
- [ ] Load testing performed

---

## 🔗 Key Files Reference

### Backend Core
- `app/app.py` - FastAPI application entry point
- `app/api_router.py` - REST API endpoints (chat, user, subjects)
- `app/lti/routes.py` - LTI 1.3 endpoints

### Frontend Core
- `frontend/src/App.tsx` - Main React component
- `frontend/src/api.ts` - Axios API client
- `frontend/vite.config.ts` - Vite configuration with proxy

### Configuration
- `.env` - Backend environment variables
- `moodle/.env` - LTI platform configuration
- `frontend/.env` - Frontend environment variables
- `docker-compose-full.yml` - Docker services orchestration

### Documentation
- `moodle/README.md` - LTI integration guide
- `moodle/PHASE_4_GUIDE.md` - Frontend integration steps
- `moodle/TESTING_IN_MOODLE_NOW.md` - Current status
- `docs/ARCHITECTURE.md` - System architecture details

---

## 📞 Next Steps

### Option 1: Implement Phase 4 (Recommended)
**Time**: 3-4 hours  
**Outcome**: Full LTI integration with chat UI in Moodle iframe

**Tasks**:
1. Create session context provider
2. Update API client with session token
3. Add backend session validation endpoint
4. Implement LTI mode UI
5. Test locally with session simulation
6. Test in Moodle with real LTI launch

### Option 2: Test Backend Only
**Time**: 30 minutes  
**Outcome**: Verify LTI backend connectivity

**Tasks**:
1. Register tool in Moodle Cloud
2. Launch from Moodle activity
3. Observe JSON response (expected)
4. Verify logs show successful JWT validation
5. Check MongoDB for created user/session

### Option 3: Both (Recommended)
1. Quick test backend connectivity (Option 2)
2. Implement Phase 4 frontend
3. Re-test with full integration

---

## 🎓 Summary

Your project is **well-architected** with a clean microservices design. The LTI backend implementation is **production-ready** (Phase 3 complete). The main gap is **Phase 4 frontend integration** to handle LTI sessions in the React app.

**Strengths**:
- ✅ Comprehensive backend implementation
- ✅ Proper separation of concerns
- ✅ Good test coverage for LTI components
- ✅ Clear documentation structure

**Areas for Improvement**:
- 🚧 Complete Phase 4 frontend LTI support
- 🔐 Secure environment variables
- 📊 Enable monitoring stack
- 🗄️ Move course mappings to database

**Overall Grade**: A- (would be A+ after Phase 4) 🎯

---

**Generated**: October 5, 2025  
**Reviewer**: GitHub Copilot  
**Status**: Ready for Phase 4 Implementation
