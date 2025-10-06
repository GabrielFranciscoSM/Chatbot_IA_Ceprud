# 🧪 Moodle LTI Integration Testing Guide

**Date**: October 6, 2025  
**Status**: Ready for Testing  
**Moodle Instance**: https://testchatbot.moodlecloud.com

---

## 📋 Prerequisites Checklist

Before testing in Moodle, ensure:

- ✅ **Services Running**: All containers up with `podman-compose -f docker-compose-full.yml up -d`
- ✅ **Public URL**: Backend accessible from internet (currently: http://150.214.22.87:8080)
- ✅ **LTI Config**: Keys generated in `lti_config/` directory
- ✅ **Environment**: `moodle/.env` configured with correct URLs
- ✅ **MongoDB**: Running and accessible

---

## 🌐 Step 1: Make Your Backend Publicly Accessible

Your backend needs to be accessible from Moodle Cloud. You have two options:

### Option A: Use Your Current Public IP (Recommended for Testing)

Your `.env` already has: `CHATBOT_BASE_URL="http://150.214.22.87:8080"`

**Verify it's accessible**:
```bash
# From another machine or your phone's browser
curl http://150.214.22.87:8080/health

# Should return: {"status": "ok", "timestamp": "..."}
```

⚠️ **Note**: HTTP (not HTTPS) might be blocked by some Moodle instances. If issues occur, use Option B.

### Option B: Use ngrok for HTTPS Tunnel (If HTTP doesn't work)

```bash
# Install ngrok if not already installed
# Download from: https://ngrok.com/download

# Start tunnel
ngrok http 8080

# You'll get a URL like: https://abc123.ngrok.io
# Update moodle/.env with this URL
```

**If using ngrok, update your environment**:
```bash
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud

# Edit moodle/.env
nano moodle/.env

# Change:
CHATBOT_BASE_URL="https://your-ngrok-url.ngrok.io"

# Restart services
podman-compose -f docker-compose-full.yml down
podman-compose -f docker-compose-full.yml up -d
```

---

## 🔧 Step 2: Verify LTI Endpoints are Working

Test that all LTI endpoints respond correctly:

```bash
# 1. Check JWKS endpoint (public key for Moodle)
curl http://150.214.22.87:8080/lti/jwks | jq .

# Expected: JSON with "keys" array containing your public key

# 2. Check LTI config endpoint
curl http://150.214.22.87:8080/lti/config | jq .

# Expected: JSON with platform configuration

# 3. Check health
curl http://150.214.22.87:8080/health | jq .

# Expected: {"status": "ok", ...}
```

**If any endpoint fails**, check:
- Services are running: `podman ps`
- Firewall allows port 8080: `sudo firewall-cmd --list-ports`
- Backend logs: `podman logs chatbot-backend`

---

## 🎓 Step 3: Register Tool in Moodle

Now register your chatbot as an external tool in Moodle:

### 3.1 Login to Moodle Admin

1. Go to: https://testchatbot.moodlecloud.com
2. Login with admin credentials
3. Navigate to: **Site Administration** → **Plugins** → **Activity modules** → **External tool** → **Manage tools**

### 3.2 Add External Tool Manually

Click **"Configure a tool manually"** and enter:

| Field | Value |
|-------|-------|
| **Tool name** | CEPRUD AI Chatbot |
| **Tool URL** | `http://150.214.22.87:8080/lti/launch` |
| **Tool description** | AI Chatbot for CEPRUD courses |
| **LTI version** | LTI 1.3 |
| **Public keyset URL** | `http://150.214.22.87:8080/lti/jwks` |
| **Initiate login URL** | `http://150.214.22.87:8080/lti/login` |
| **Redirection URI(s)** | `http://150.214.22.87:8080/lti/launch` |

### 3.3 Configure Tool Settings

**Default launch container**: New window OR Embed (recommended)

**Services**: (Optional, can leave default)
- ☑ IMS LTI Assignment and Grade Services
- ☑ IMS LTI Names and Role Provisioning Services

**Privacy**:
- ☑ Share launcher's name with tool
- ☑ Share launcher's email with tool
- ☑ Accept grades from the tool (optional)

### 3.4 Get Client ID

After saving, Moodle will show you the tool details including:
- **Client ID**: Copy this (e.g., "GBx1F4LefiUr7bZ")
- **Platform ID**: Should match your Moodle URL
- **Deployment ID**: Usually "1"

**Verify these match your `.env` file**:
```bash
cat moodle/.env | grep CLIENT_ID
# Should show: MOODLE_CLIENT_ID="GBx1F4LefiUr7bZ"
```

---

## 📚 Step 4: Add Chatbot to a Course

### 4.1 Create or Select a Course

1. Go to your Moodle dashboard
2. Create a new course or select an existing one
3. **Important**: Set the course **"Short name"** to match your subject mapping
   - For example: **"IS"** for Ingeniería de Servidores
   - Check `moodle/.env` for available mappings

**Available mappings**:
```json
{
  "IS": "ingenieria_de_servidores",
  "MAC": "modelos_avanzados_computacion",
  "MH": "metaheuristicas",
  "SO": "sistemas_operativos",
  "IC": "ingenieria_conocimiento",
  "ALG": "algorítmica",
  "CALC": "calculo"
}
```

### 4.2 Add External Tool Activity

1. Turn editing on
2. Click **"Add an activity or resource"**
3. Select **"External tool"**
4. Configure:
   - **Activity name**: "CEPRUD AI Assistant" (or similar)
   - **Preconfigured tool**: Select "CEPRUD AI Chatbot"
   - **Launch container**: Embed or New window
   - **Privacy**: Share name and email
5. Save and display

---

## 🚀 Step 5: Test LTI Launch

### 5.1 Launch the Tool

1. Click on the external tool activity you just created
2. Moodle should redirect you to your chatbot
3. You should see:
   - ✅ Your chatbot interface loads
   - ✅ User is auto-logged in (shows your email)
   - ✅ Subject is auto-selected (based on course short name)
   - ✅ LTI mode indicator (if you added one)
   - ✅ No errors in browser console

### 5.2 Expected Behavior

**What should happen**:
1. Moodle initiates LTI login → `/lti/login`
2. Backend redirects to Moodle for authentication
3. Moodle sends JWT token → `/lti/launch`
4. Backend validates JWT and creates session
5. Frontend receives session token
6. User sees chatbot interface with:
   - Email: Your Moodle email
   - Subject: Auto-selected based on course
   - Ready to chat

**LTI Launch Flow**:
```
Moodle Course → Click Activity
       ↓
POST /lti/login (OIDC initiation)
       ↓
Redirect to Moodle Auth
       ↓
POST /lti/launch (JWT token)
       ↓
Validate JWT + Create Session
       ↓
Redirect to Frontend with session_token
       ↓
Frontend loads with LTI context
```

### 5.3 Test Chat Functionality

Once loaded, test the chatbot:

1. **Send a test message**: "Hola, ¿qué temas cubre esta asignatura?"
2. **Check response**: Should get relevant answer from RAG
3. **Check session persistence**: Refresh page, messages should persist
4. **Check sources**: Response should include document sources

---

## 🐛 Step 6: Troubleshooting

### Issue: "Invalid JWT signature"

**Symptoms**: Error message after clicking activity  
**Cause**: Moodle can't verify your JWT signature

**Solutions**:
```bash
# 1. Verify JWKS endpoint is accessible from Moodle
curl http://150.214.22.87:8080/lti/jwks

# 2. Check keys exist
ls -la lti_config/
# Should show: private_key.pem, public_key.pem, jwks.json

# 3. Regenerate keys if needed
./setup_lti.sh

# 4. Update tool configuration in Moodle with new JWKS URL
```

---

### Issue: "Platform not configured"

**Symptoms**: Error in backend logs  
**Cause**: Platform ID mismatch

**Solutions**:
```bash
# 1. Check backend logs
podman logs chatbot-backend | grep -i "platform"

# 2. Verify .env configuration
cat moodle/.env | grep PLATFORM_ID
# Should match: https://testchatbot.moodlecloud.com

# 3. Check MongoDB for platform config
podman exec -it mongodb mongosh
use chatbot
db.lti_platforms.find().pretty()

# Should show your platform configuration
```

---

### Issue: "Subject not mapped"

**Symptoms**: Chatbot loads but no subject selected  
**Cause**: Course short name doesn't match mappings

**Solutions**:
```bash
# 1. Check course short name in Moodle
# Go to Course → Settings → Course short name

# 2. Check available mappings
cat moodle/.env | grep DEFAULT_SUBJECT_MAPPINGS

# 3. Add new mapping or change course short name

# Example: Add "TEST" mapping
# Edit moodle/.env and add to DEFAULT_SUBJECT_MAPPINGS:
# "TEST": "ingenieria_de_servidores"

# 4. Restart backend
podman restart chatbot-backend
```

---

### Issue: "CORS errors" in browser console

**Symptoms**: Frontend can't connect to backend  
**Cause**: CORS configuration

**Solutions**:
```bash
# 1. Check CORS is configured in app.py
podman logs chatbot-backend | grep CORS

# 2. Verify frontend URL is allowed
# Check app/app.py for CORS origins

# 3. If using ngrok, update CORS to allow ngrok URL
```

---

### Issue: "Connection refused"

**Symptoms**: Can't connect to backend  
**Cause**: Firewall or network issue

**Solutions**:
```bash
# 1. Check services are running
podman ps

# 2. Check port is open
sudo firewall-cmd --list-ports
# Should show: 8080/tcp

# 3. Add port if needed
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# 4. Test from external network
curl http://150.214.22.87:8080/health
```

---

### Issue: Frontend shows blank page

**Symptoms**: White screen after LTI launch  
**Cause**: Session token invalid or frontend error

**Solutions**:
```bash
# 1. Check frontend logs
podman logs chatbot-frontend

# 2. Check browser console for errors
# Open DevTools (F12) and check Console tab

# 3. Verify session token in URL
# URL should have: ?session_token=...&lti=true

# 4. Test session validation
curl -H "X-Session-Token: <token_from_url>" \
     http://150.214.22.87:8080/session/validate | jq .
```

---

## 📊 Step 7: Monitor and Verify

### Check Backend Logs

```bash
# Watch logs in real-time
podman logs -f chatbot-backend

# Filter for LTI-related logs
podman logs chatbot-backend | grep -i lti

# Check for errors
podman logs chatbot-backend | grep -i error
```

### Check MongoDB Sessions

```bash
# Connect to MongoDB
podman exec -it mongodb mongosh

# Switch to chatbot database
use chatbot

# View LTI sessions
db.lti_sessions.find().pretty()

# View user sessions
db.user_sessions.find().pretty()

# Count sessions
db.lti_sessions.countDocuments()
```

### Check Frontend Access

```bash
# Verify frontend is accessible
curl http://localhost:8090/

# Should return HTML with your app
```

---

## ✅ Success Criteria

Your integration is working correctly if:

- ✅ Clicking the activity in Moodle loads your chatbot
- ✅ User email is auto-filled from Moodle profile
- ✅ Subject is auto-selected based on course
- ✅ Chat messages send and receive correctly
- ✅ RAG responses include relevant content
- ✅ Session persists across page refreshes
- ✅ No errors in browser console
- ✅ No errors in backend logs

---

## 🎯 Next Steps After Successful Testing

Once testing in Moodle works:

### 1. Production Deployment
- Get SSL certificate (Let's Encrypt)
- Use HTTPS instead of HTTP
- Set up proper domain name
- Configure production MongoDB

### 2. Security Hardening
- Enable rate limiting
- Add request validation
- Implement audit logging
- Set up monitoring

### 3. User Acceptance Testing
- Test with real students
- Gather feedback
- Monitor usage metrics
- Optimize performance

### 4. Documentation
- Create user guide for teachers
- Create student tutorial
- Document admin procedures

---

## 📞 Support Resources

### Useful Commands Reference

```bash
# Restart all services
podman-compose -f docker-compose-full.yml restart

# View all logs
podman-compose -f docker-compose-full.yml logs

# Stop everything
podman-compose -f docker-compose-full.yml down

# Start fresh (removes volumes)
podman-compose -f docker-compose-full.yml down -v
podman-compose -f docker-compose-full.yml up -d

# Create new test session
.venv/bin/python moodle/create_test_session.py
```

### Log Files to Check

- **Backend**: `podman logs chatbot-backend`
- **Frontend**: `podman logs chatbot-frontend`
- **MongoDB**: `podman logs mongodb`
- **RAG Service**: `podman logs rag-service`

### Debugging Tools

- **Browser DevTools**: F12 → Console, Network tabs
- **MongoDB Compass**: GUI for MongoDB (optional)
- **Postman**: Test API endpoints directly
- **ngrok inspect**: http://localhost:4040 (if using ngrok)

---

## 🎓 Moodle LTI Resources

- [Moodle LTI Documentation](https://docs.moodle.org/en/External_tool)
- [LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [Moodle External Tool Settings](https://docs.moodle.org/en/External_tool_settings)

---

**Good luck with your Moodle testing! 🚀**

If you encounter issues, check the troubleshooting section above or review the logs for specific error messages.
