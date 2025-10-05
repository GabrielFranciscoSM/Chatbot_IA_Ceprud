# Phase 3 Integration Complete

## Summary
Phase 3 of the LTI integration has been implemented. The `/lti/launch` endpoint now includes:

1. **JWT Validation** - Using `LTIJWTValidator` to verify tokens from Moodle
2. **User Management** - Using `LTIUserService` to create/update users in MongoDB
3. **Session Management** - Using `LTISessionService` to manage sessions with MongoDB
4. **Course Mapping** - Maps Moodle courses to chatbot subjects
5. **Auto-redirect** - Redirects to chat UI with session token

## Files Modified/Created

### Core Integration Files
- ✅ `app/lti/routes.py` - Updated `/lti/launch` endpoint with full integration
- ✅ `app/lti/database.py` - MongoDB connection helper for LTI services
- ✅ `app/lti/user_service.py` - Simplified user management service
- ✅ `app/lti/session_service.py` - MongoDB-backed session service

### Test Files
- ✅ `moodle/test_phase3.py` - Comprehensive test script
- ✅ `moodle/test_phase3_quick.py` - Quick import validation test

### Documentation
- ✅ `moodle/PHASE_3_SUMMARY.md` - Complete Phase 3 documentation

## Key Features Implemented

### 1. JWT Validation (`app/lti/jwt_validator.py`)
```python
class LTIJWTValidator:
    async def validate_token(self, token: str) -> Dict
    async def _get_moodle_public_key(self, kid: str) -> str
    def _validate_claims(self, decoded: Dict) -> None
```

### 2. User Service (`app/lti/user_service.py`)
```python
class LTIUserService:
    async def create_or_update_user(
        lti_user_id, email, name, given_name, family_name
    ) -> Dict
```

### 3. Session Service (`app/lti/session_service.py`)
```python
class LTISessionService:
    async def create_or_get_session(
        user_id, lti_user_id, context_id, context_label, subject
    ) -> Dict
    async def get_session(session_token) -> Optional[Dict]
    async def delete_session(session_token) -> bool
    async def cleanup_expired_sessions()
```

### 4. Launch Flow (`app/lti/routes.py`)
```python
@router.post("/lti/launch")
async def lti_launch(request: Request):
    # 1. Parse id_token from form
    # 2. Validate JWT
    # 3. Extract user and course claims
    # 4. Create/update user in MongoDB
    # 5. Map course to subject
    # 6. Create/retrieve session
    # 7. Redirect to chat UI with session token
```

## Testing

### Quick Test (Imports Only)
```bash
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud
.venv/bin/python moodle/test_phase3_quick.py
```

### Full Test (With MongoDB)
```bash
# Ensure MongoDB is running
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud
.venv/bin/python moodle/test_phase3.py
```

### Test with Running Server
```bash
# Terminal 1: Start server
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud/app
../.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8080

# Terminal 2: Test endpoints
curl http://localhost:8080/lti/jwks
curl http://localhost:8080/lti/login
```

## Configuration Required

### Environment Variables
```bash
# In moodle/.env or system environment
MOODLE_ISSUER=https://moodle.ugr.es
MOODLE_CLIENT_ID=your_client_id
MOODLE_JWKS_URL=https://moodle.ugr.es/mod/lti/certs.php
CHATBOT_BASE_URL=http://localhost:8080
FRONTEND_URL=http://localhost:5173
MONGO_URI=mongodb://localhost:27017
```

### Course-to-Subject Mapping
Edit `app/lti/routes.py` and update:
```python
COURSE_SUBJECT_MAPPING = {
    "ASIG001": "Matematicas",
    "ASIG002": "Fisica",
    # Add your course mappings here
}
```

## MongoDB Collections

### Users Collection (`users`)
No schema changes - uses existing collection.

### LTI Sessions Collection (`lti_sessions`)
```json
{
  "_id": ObjectId,
  "session_token": "secure_random_token",
  "user_id": "user_mongodb_id",
  "lti_user_id": "lti_platform_user_id",
  "context_id": "moodle_course_id",
  "context_label": "ASIG001",
  "subject": "Matematicas",
  "created_at": ISODate,
  "last_activity": ISODate,
  "expires_at": ISODate
}
```

## Next Steps

### Phase 4: Frontend Integration
- [ ] Update React frontend to handle `?session_token=` parameter
- [ ] Support LTI mode (`?lti=true`)
- [ ] Display course/subject context
- [ ] Handle iframe embedding properly
- [ ] Add session-based authentication

### Phase 5: Moodle Configuration
- [ ] Configure External Tool in Moodle
- [ ] Set up LTI 1.3 registration
- [ ] Add JWKS URL from chatbot
- [ ] Test real LTI launch from Moodle
- [ ] Add activity to courses

### Phase 6: Production Readiness
- [ ] HTTPS/SSL certificates
- [ ] Production MongoDB configuration
- [ ] Key rotation mechanism
- [ ] Enhanced logging and monitoring
- [ ] Error handling improvements
- [ ] Rate limiting for LTI endpoints
- [ ] Session cleanup background task

## Verification Checklist

- ✅ JWT validator class created
- ✅ User service integrated with existing MongoDB
- ✅ Session service with MongoDB persistence
- ✅ Database connection helper created
- ✅ `/lti/launch` endpoint fully implemented
- ✅ Course-to-subject mapping system
- ✅ HTML redirect for iframe compatibility
- ✅ Test scripts created
- ✅ Documentation updated

## Known Limitations

1. **JWT Validation**: Currently uses our own keys for testing. In production, needs to fetch Moodle's public keys from JWKS endpoint.

2. **Nonce Storage**: Nonce validation is implemented but needs persistent storage (Redis/MongoDB) for production.

3. **Course Mappings**: Currently hardcoded in routes.py. Should move to configuration file or database.

4. **Session Cleanup**: No background task to clean expired sessions yet. Should add periodic cleanup.

5. **Frontend**: Not yet updated to handle LTI session tokens and embedded mode.

## Status

✅ **Phase 3 COMPLETE**

The backend LTI integration is fully implemented and ready for testing with a real Moodle instance. The next phase focuses on frontend changes to complete the user experience.
