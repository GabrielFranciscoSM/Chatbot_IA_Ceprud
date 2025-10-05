# Phase 3: Complete LTI Integration

## Overview
Phase 3 completes the LTI integration by:
1. Implementing JWT signature validation
2. Creating/updating users in MongoDB from LTI claims
3. Managing sessions with MongoDB persistence
4. Mapping Moodle courses to chatbot subjects
5. Redirecting to the chat UI with session tokens

## Changes Made

### 1. Database Connection (`app/lti/database.py`)
- Created MongoDB connection helper for LTI services
- Provides singleton client pattern
- Supports environment-based configuration

### 2. Updated LTI Routes (`app/lti/routes.py`)
**Imports:**
- Added `JWTValidator`, `LTIUserService`, `LTISessionService`
- Added `HTMLResponse` for iframe-friendly redirects
- Added `datetime` for timestamp handling

**Course-Subject Mapping:**
```python
COURSE_SUBJECT_MAPPING = {
    "ASIG001": "Matematicas",
    "ASIG002": "Fisica",
    # Add more mappings as needed
}
```

**Updated `/lti/launch` endpoint:**
- Validates JWT with signature verification
- Extracts user claims (email, name, given_name, family_name)
- Extracts context (course) information
- Creates or updates user in MongoDB
- Maps course label to subject
- Creates or retrieves session with token
- Returns HTML redirect to chat UI with session token

### 3. Simplified User Service (`app/lti/user_service.py`)
**Method: `create_or_update_user()`**
- Takes LTI user claims as parameters
- Checks for existing user by email
- Creates new user if not found
- Uses existing `services.user_service` for MongoDB operations
- Returns user document

### 4. Session Service with MongoDB (`app/lti/session_service.py`)
**Method: `create_or_get_session()`**
- Creates or retrieves session for user+context combination
- Generates secure session token using `secrets.token_urlsafe()`
- Stores sessions in MongoDB `lti_sessions` collection
- Session expires after 8 hours
- Updates last_activity on each access

**Method: `get_session()`**
- Retrieves session by token
- Validates expiration
- Updates last_activity

**Method: `cleanup_expired_sessions()`**
- Removes expired sessions from database

## Flow Diagram

```
Moodle → /lti/login → OIDC Redirect → Moodle Auth
                                            ↓
                                    POST /lti/launch (id_token)
                                            ↓
                                    ┌───────────────────┐
                                    │ Validate JWT      │
                                    │ - Signature       │
                                    │ - Claims          │
                                    └───────┬───────────┘
                                            ↓
                                    ┌───────────────────┐
                                    │ Extract Claims    │
                                    │ - User info       │
                                    │ - Course info     │
                                    └───────┬───────────┘
                                            ↓
                                    ┌───────────────────┐
                                    │ Create/Get User   │
                                    │ (MongoDB)         │
                                    └───────┬───────────┘
                                            ↓
                                    ┌───────────────────┐
                                    │ Map Course →      │
                                    │ Subject           │
                                    └───────┬───────────┘
                                            ↓
                                    ┌───────────────────┐
                                    │ Create Session    │
                                    │ (MongoDB)         │
                                    └───────┬───────────┘
                                            ↓
                                    HTML Redirect to Chat UI
                                    (?session_token=...&lti=true&subject=...)
```

## Testing

### Run Test Script
```bash
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud/moodle
python test_phase3.py
```

This will test:
1. Service initialization
2. JWT token creation
3. JWT validation
4. User creation/retrieval
5. Session creation
6. Session retrieval

### Manual Testing with Server
1. Start the FastAPI server:
```bash
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud
source .venv/bin/activate
cd app
uvicorn app:app --host 0.0.0.0 --port 8080
```

2. Test endpoints:
- JWKS: http://localhost:8080/lti/jwks
- Login: http://localhost:8080/lti/login
- Launch: POST to http://localhost:8080/lti/launch (with id_token)

## Configuration

### Environment Variables
```bash
# Moodle Configuration
MOODLE_ISSUER=https://moodle.ugr.es
MOODLE_CLIENT_ID=your_client_id
MOODLE_AUTH_LOGIN_URL=https://moodle.ugr.es/mod/lti/auth.php
MOODLE_JWKS_URL=https://moodle.ugr.es/mod/lti/certs.php

# Chatbot Configuration
CHATBOT_BASE_URL=http://localhost:8080
FRONTEND_URL=http://localhost:5173

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGODB_DATABASE=chatbot_users

# LTI Keys
LTI_CONFIG_DIR=./lti_config
```

### Course Mappings
Edit `app/lti/routes.py` to add course-to-subject mappings:
```python
COURSE_SUBJECT_MAPPING = {
    "IS2024": "Ingenieria del Software",
    "MATH101": "Matematicas I",
    "PHYS201": "Fisica",
}
```

## MongoDB Collections

### `users`
Existing collection, now includes LTI users:
```json
{
  "_id": ObjectId("..."),
  "email": "student@ugr.es",
  "name": "John Doe",
  "role": "student",
  "created_at": ISODate("..."),
  "subjects": []
}
```

### `lti_sessions` (new)
Stores LTI session data:
```json
{
  "_id": ObjectId("..."),
  "session_token": "random_secure_token",
  "user_id": "user_object_id",
  "lti_user_id": "lti_user_123",
  "context_id": "course-001",
  "context_label": "ASIG001",
  "subject": "Matematicas",
  "created_at": ISODate("..."),
  "last_activity": ISODate("..."),
  "expires_at": ISODate("...")
}
```

## Security Features

1. **JWT Validation:**
   - Signature verification using Moodle's public keys
   - Claims validation (iss, aud, exp, nonce)
   - Nonce replay protection

2. **Session Security:**
   - Cryptographically secure tokens (`secrets.token_urlsafe()`)
   - 8-hour expiration
   - Automatic cleanup of expired sessions

3. **User Privacy:**
   - No passwords stored (SSO via LTI)
   - Email used as unique identifier
   - LTI user ID stored for mapping

## Next Steps

### Phase 4: Frontend Integration
1. Update React frontend to handle LTI mode
2. Support session token authentication
3. Display course/subject context
4. Handle iframe embedding

### Phase 5: Moodle Plugin
1. Create Moodle external tool configuration
2. Configure LTI 1.3 settings
3. Test in real Moodle environment
4. Add activity to courses

### Phase 6: Production Deployment
1. HTTPS/SSL certificates
2. Production MongoDB setup
3. Key rotation strategy
4. Monitoring and logging
5. Error handling improvements

## Troubleshooting

### JWT Validation Fails
- Verify Moodle's JWKS URL is accessible
- Check that `MOODLE_ISSUER` matches exactly
- Ensure clocks are synchronized (JWT exp/iat)

### User Creation Fails
- Check MongoDB connection
- Verify `MONGO_URI` is correct
- Ensure user service is running

### Session Not Found
- Check session hasn't expired (8 hour limit)
- Verify MongoDB connection
- Check session token is passed correctly

### Redirect Issues in iframe
- Using HTML redirect instead of HTTP redirect
- Check CORS settings
- Verify `FRONTEND_URL` is correct
- Test with X-Frame-Options headers

## Files Modified/Created

- ✓ `app/lti/routes.py` - Updated launch endpoint
- ✓ `app/lti/database.py` - New MongoDB connection
- ✓ `app/lti/user_service.py` - Simplified for existing user service
- ✓ `app/lti/session_service.py` - MongoDB-backed sessions
- ✓ `moodle/test_phase3.py` - Test script
- ✓ `moodle/PHASE_3_SUMMARY.md` - This document
