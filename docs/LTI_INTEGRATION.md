# LTI 1.3 Integration Guide

## 📚 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

---

## Overview

This chatbot supports **LTI 1.3 (Learning Tools Interoperability)** integration, allowing seamless embedding within Learning Management Systems like Moodle. Students can access the chatbot directly from their courses without additional authentication.

### Key Features

✅ **OIDC Authentication** - Secure OAuth 2.0 flow
✅ **Context-aware** - Automatically maps courses to chatbot subjects
✅ **Session Management** - MongoDB-backed persistent sessions
✅ **JWT Validation** - Cryptographic verification of launch requests
✅ **Iframe Support** - Proper security headers for embedding
✅ **HTTPS Ready** - Production-ready with SSL support

---

## Architecture

### LTI 1.3 Flow

```
┌─────────┐           ┌──────────┐           ┌─────────┐
│ Student │           │  Moodle  │           │ Chatbot │
└────┬────┘           └────┬─────┘           └────┬────┘
     │                     │                      │
     │  1. Click Activity  │                      │
     ├────────────────────>│                      │
     │                     │                      │
     │                     │  2. POST /lti/login  │
     │                     ├─────────────────────>│
     │                     │                      │
     │                     │  3. 302 Redirect     │
     │                     │<─────────────────────┤
     │                     │  (to auth endpoint)  │
     │                     │                      │
     │  4. Auth Request    │                      │
     │<────────────────────┤                      │
     │                     │                      │
     │  5. POST /lti/launch (with id_token)      │
     ├───────────────────────────────────────────>│
     │                     │                      │
     │                     │  6. Validate JWT     │
     │                     │      Create Session  │
     │                     │      Map Subject     │
     │                     │                      │
     │  7. Redirect to Frontend                   │
     │<───────────────────────────────────────────┤
     │  (with session_token)                      │
     │                     │                      │
     │  8. Load Chatbot UI │                      │
     │<───────────────────────────────────────────┤
     │                     │                      │
```

### Components

#### **Backend Endpoints** (`app/lti/routes.py`)

- **`GET/POST /api/lti/login`** - OIDC login initiation
- **`POST /api/lti/launch`** - Tool launch with JWT validation
- **`GET /api/lti/jwks`** - Public key set for Moodle
- **`GET /api/session/validate`** - Session validation for frontend

#### **LTI Services**

- **`LTIConfig`** - Manages RSA keys and JWKS
- **`LTIJWTValidator`** - Validates and decodes JWT tokens
- **`LTIUserService`** - Creates/updates users from LTI data
- **`LTISessionService`** - Manages MongoDB-backed sessions

#### **Frontend Integration** (`frontend/src/contexts/SessionContext.tsx`)

- Parses URL parameters (`session_token`, `lti`, `subject`)
- Validates session with backend
- Displays simplified UI for LTI mode
- Shows course context banner

---

## Setup

### Prerequisites

- **Moodle** instance (Cloud or self-hosted) with admin access
- **HTTPS** endpoint for the chatbot (required by Moodle)
- **MongoDB** for session storage
- **RSA key pair** for JWT signing

### 1. Generate RSA Keys

```bash
# Create directory for LTI config
mkdir -p lti_config

# Generate private key
openssl genrsa -out lti_config/private_key.pem 2048

# Generate public key
openssl rsa -in lti_config/private_key.pem -pubout -out lti_config/public_key.pem

# Generate JWKS (done automatically by the application)
```

### 2. Configure Environment Variables

Edit `.env`:

```bash
# LTI / Moodle Configuration
MOODLE_ISSUER="https://your-moodle.example.com"
MOODLE_AUTH_LOGIN_URL="https://your-moodle.example.com/mod/lti/auth.php"
MOODLE_JWKS_URL="https://your-moodle.example.com/mod/lti/certs.php"
MOODLE_CLIENT_ID="your_client_id_from_moodle"
CHATBOT_BASE_URL="https://your-chatbot-domain.example.com"
FRONTEND_URL="https://your-chatbot-domain.example.com"

# LTI Config Directory
LTI_CONFIG_DIR="./lti_config"
```

### 3. Configure Moodle External Tool

#### As Moodle Administrator:

1. Navigate to: `Site administration > Plugins > Activity modules > External tool > Manage tools`
2. Click **"Configure a tool manually"**
3. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Tool name** | Chatbot CEPRUD |
   | **Tool URL** | `https://your-domain.example.com/api/lti/launch` |
   | **LTI version** | LTI 1.3 |
   | **Public keyset URL** | `https://your-domain.example.com/api/lti/jwks` |
   | **Initiate login URL** | `https://your-domain.example.com/api/lti/login` |
   | **Redirection URI(s)** | `https://your-domain.example.com/api/lti/launch` |
   | **Supports Deep Linking** | No (optional) |
   | **Content selection URL** | Leave empty |

4. **Save changes**
5. Copy the generated **Client ID**
6. Update `.env` with the `MOODLE_CLIENT_ID`

### 4. Setup HTTPS

Moodle requires HTTPS. Choose one option:

#### Option A: Cloudflare Tunnel (Development/Testing)

```bash
# Install cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Start tunnel (frontend)
cloudflared tunnel --url http://localhost:8090

# Copy the generated HTTPS URL to .env as CHATBOT_BASE_URL and FRONTEND_URL
```

**Helper Scripts:**
```bash
# Start tunnel
./start-tunnel.sh

# Stop tunnel
./stop-tunnel.sh
```

#### Option B: Nginx + Let's Encrypt (Production)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.example.com

# Configure nginx reverse proxy to frontend:8090
```

#### Option C: Platform-as-a-Service

Deploy to platforms with built-in SSL:
- Railway
- Render
- Heroku
- Digital Ocean App Platform

### 5. Deploy Services

```bash
# Build and start all services
docker-compose -f docker-compose-full.yml up --build -d

# Check logs
docker-compose -f docker-compose-full.yml logs -f backend frontend
```

---

## Configuration

### Subject Mapping

Configure course-to-subject mapping in `app/lti/routes.py`:

```python
COURSE_SUBJECT_MAPPING = {
    # Moodle course label -> Chatbot subject ID
    "IS": "ingenieria_de_servidores",
    "MAC": "modelos_avanzados_computacion",
    "META": "metaheuristicas",
    "IE1": "inferencia_estadistica_1",
    "EST": "estadistica",
}
```

**How it works:**
1. Moodle sends the course **label** (e.g., "IS") in the JWT
2. Backend maps it to the chatbot **subject ID** (e.g., "ingenieria_de_servidores")
3. Frontend loads the appropriate subject for RAG retrieval

### Session Configuration

Sessions are stored in MongoDB with:
- **Expiration**: 8 hours (configurable in `LTISessionService`)
- **Fields**: user_id, lti_user_id, context_id, context_label, subject, session_token
- **Updates**: Last activity timestamp on each validation

To change session expiration:

```python
# In app/lti/session_service.py
"expires_at": datetime.utcnow() + timedelta(hours=8)  # Change hours here
```

### User Management

Users are automatically created/updated from Moodle with:
- **Email**: From JWT `email` claim
- **Name**: From JWT `name` claim
- **Role**: Default "student" (can be enhanced with LTI role claims)

---

## Testing

### 1. Test Endpoints Manually

#### JWKS Endpoint
```bash
curl https://your-domain.example.com/api/lti/jwks | jq .
```

Expected response:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "kid": "lti-key-1",
      "n": "...",
      "e": "AQAB",
      "alg": "RS256"
    }
  ]
}
```

#### Health Check
```bash
curl https://your-domain.example.com/health
```

### 2. Add Activity to Moodle Course

1. Go to a course as teacher
2. Turn editing on
3. "Add an activity or resource"
4. Select "External tool"
5. Choose "Chatbot CEPRUD" (preconfigured tool)
6. Set activity name and save

### 3. Launch as Student

1. Enroll as student in the course
2. Click the chatbot activity
3. You should see:
   - Brief loading screen
   - Chatbot interface loads with course context
   - Course name shown in context banner
   - Subject automatically selected

### 4. Check Browser Console

Look for these logs:
```
SessionContext: Parsing URL parameters {token: true, lti: true, subject: "..."}
SessionContext: LTI mode detected, validating session...
SessionContext: Session validated successfully {...}
App: Applying LTI session data after validation
App: Setting subject from validated LTI session: ...
```

### 5. Check Backend Logs

```bash
docker-compose logs backend | grep "LTI"
```

Look for:
```
LTI LOGIN DEBUG - Received params: {...}
JWT DECODED CLAIMS - Email: ..., Name: ...
SUBJECT MAPPING - Context Label: IS, Mapped Subject ID: ingenieria_de_servidores
LTI LAUNCH - Final Redirect - Full Redirect URL: ...
Session validated successfully
```

---

## Troubleshooting

### "Invalid request" error in Moodle iframe

**Cause**: Mismatch in redirect URIs

**Solution**:
1. Verify `Redirection URI(s)` in Moodle matches `CHATBOT_BASE_URL/api/lti/launch`
2. Check `.env` has correct `CHATBOT_BASE_URL`
3. Ensure no trailing slashes

### "Missing id_token" error

**Cause**: Missing `response_mode=form_post` in OIDC request

**Solution**:
- This is fixed in the code - ensure you're using the latest version
- Check logs show: `response_mode=form_post` in the OIDC URL

### JWT validation fails

**Causes**:
- Wrong `MOODLE_ISSUER` or `MOODLE_CLIENT_ID`
- Moodle can't fetch JWKS from chatbot
- Network/firewall issues

**Solutions**:
1. Verify issuer URL matches Moodle exactly: `https://your-moodle.example.com`
2. Test JWKS endpoint is publicly accessible
3. Check Moodle logs for connection errors

### Mixed content warnings

**Cause**: Frontend tries to load HTTP resources from HTTPS page

**Solution**:
- Ensure all URLs in `.env` use `https://`
- Update `CHATBOT_BASE_URL` and `FRONTEND_URL` to HTTPS

### Session not found / 404 error

**Causes**:
- MongoDB connection failure
- Session expired
- User ID is None

**Solutions**:
1. Check MongoDB is running: `docker-compose ps mongo-service`
2. Verify MongoDB connection in logs
3. Check user-service is returning valid user IDs

### Chatbot shows "Selecciona una asignatura"

**Causes**:
- Subject not mapped correctly
- Frontend not receiving subject from session
- Subject ID doesn't match `SUBJECTS` array

**Solutions**:
1. Check `COURSE_SUBJECT_MAPPING` has the course label
2. Verify frontend console shows correct subject ID
3. Ensure subject ID matches `frontend/src/constants.ts`

### Can't type in chat input

**Causes**:
- `selectedSubject` is empty
- Email validation failing
- `currentSession` is null

**Solutions**:
1. Check browser console for session validation success
2. Hard refresh browser (Ctrl+Shift+R)
3. Verify frontend was rebuilt with latest code

---

## Security

### JWT Validation

The chatbot validates JWT tokens from Moodle:

✅ **Signature verification** using Moodle's public keys  
✅ **Issuer validation** (`iss` claim matches `MOODLE_ISSUER`)  
✅ **Audience validation** (`aud` claim matches `MOODLE_CLIENT_ID`)  
✅ **Expiration check** (`exp` claim)  
✅ **Nonce validation** (prevents replay attacks)  
✅ **Required claims** (sub, email, name, context, resource_link)

### Session Security

✅ **Random tokens** (32-byte URL-safe tokens)  
✅ **Expiration** (8 hours, configurable)  
✅ **MongoDB storage** (not in client cookies)  
✅ **Activity tracking** (last_activity timestamp)

### HTTPS/TLS

✅ **Required by Moodle** for LTI 1.3  
✅ **Cloudflare Tunnel** provides free SSL  
✅ **Let's Encrypt** for production deployments  
✅ **Headers configured** (CSP, HSTS, etc.)

### iframe Security

```nginx
# In nginx.conf
add_header Content-Security-Policy "frame-ancestors *" always;
add_header X-Content-Type-Options "nosniff" always;
```

**Note**: `frame-ancestors *` allows embedding from any origin. In production, restrict to your Moodle domain:

```nginx
add_header Content-Security-Policy "frame-ancestors https://your-moodle.example.com" always;
```

---

## Advanced Configuration

### Custom User Attributes

Enhance user creation with LTI role claims:

```python
# In app/lti/routes.py, lti_launch endpoint

roles = decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])

# Map LTI roles to chatbot roles
role = "student"  # default
if "Instructor" in str(roles):
    role = "teacher"
elif "Administrator" in str(roles):
    role = "admin"

user = await user_service.create_or_update_user(
    lti_user_id=lti_user_id,
    email=email,
    name=name,
    role=role  # Pass custom role
)
```

### Deep Linking (Optional)

For content selection within Moodle (advanced):

1. Enable in Moodle tool configuration
2. Implement `/lti/deep-link` endpoint
3. Return content items in LTI Deep Linking format

### Analytics Integration

Track LTI launches in analytics:

```python
# In lti_launch endpoint, after session creation

await logging_service.log_event(
    event_type="lti_launch",
    user_id=user_id,
    context_id=context_id,
    metadata={
        "course_label": context_label,
        "subject": subject,
        "lti_user_id": lti_user_id
    }
)
```

---

## Resources

- **LTI 1.3 Specification**: https://www.imsglobal.org/spec/lti/v1p3/
- **Moodle LTI Documentation**: https://docs.moodle.org/en/LTI_and_Moodle
- **JWT Debugging**: https://jwt.io/
- **Cloudflare Tunnel Docs**: https://developers.cloudflare.com/cloudflare-one/

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review backend logs: `docker-compose logs backend`
3. Check Moodle logs (Site administration > Reports > Logs)
4. Open a GitHub issue with logs and configuration (remove sensitive data)

---

*Last updated: October 2025 - Version 3.0*
