# 🧪 Testing LTI Integration in Moodle Cloud NOW

## Current Status: Partially Testable

You can test the **registration and initial connection**, but the full launch won't work yet.

---

## ✅ What You CAN Test Right Now

### 1. **Tool Registration**
You can register the chatbot in Moodle and verify the configuration is correct.

### 2. **JWKS Endpoint**
Moodle can fetch your public keys to verify JWT signatures.

### 3. **OIDC Redirect**
Clicking the tool will trigger the OIDC authentication flow.

---

## 🚧 What WON'T Work Yet

### 1. **Complete Launch Flow**
After Moodle redirects back with the JWT, the chatbot will:
- ❌ Show JSON response instead of chat UI
- ❌ Not create/login users
- ❌ Not persist sessions
- ❌ Not redirect to embedded chat

### 2. **User Experience**
- ❌ Students won't see the chat interface
- ❌ No auto-login
- ❌ No course-to-subject mapping in UI

---

## 📋 Step-by-Step: Register in Moodle Cloud

### Prerequisites

1. **Make sure your server is accessible from internet**
   ```bash
   # Test from external network
   curl http://150.214.22.87:8080/lti/jwks
   ```

2. **If not accessible, use ngrok:**
   ```bash
   # Start server
   cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud/app
   ../.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8080
   
   # In another terminal
   ngrok http 8080
   
   # Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   # Update CHATBOT_BASE_URL in moodle/.env
   ```

---

### Step 1: Access Moodle Site Administration

1. Log in to `https://testchatbot.moodlecloud.com`
2. Go to **Site administration**
3. Navigate to: **Plugins → Activity modules → External tool → Manage tools**

---

### Step 2: Register the Tool

Click **"Configure a tool manually"** and enter:

| Field | Value |
|-------|-------|
| **Tool name** | `CEPRUD AI Chatbot` |
| **Tool URL** | `http://150.214.22.87:8080/lti/launch` |
| **LTI version** | `LTI 1.3` |
| **Public keyset URL** | `http://150.214.22.87:8080/lti/jwks` |
| **Initiate login URL** | `http://150.214.22.87:8080/lti/login` |
| **Redirection URI(s)** | `http://150.214.22.87:8080/lti/launch` |

**If using ngrok, replace the URLs:**
```
http://150.214.22.87:8080  →  https://your-ngrok-url.ngrok.io
```

---

### Step 3: Configure Tool Settings

#### **Privacy Settings** (Important!)
- ✅ **Share launcher's name with tool**: YES
- ✅ **Share launcher's email with tool**: YES
- ✅ **Accept grades from the tool**: Optional (not used yet)

#### **Default Launch Container**
- Select: **New window** (for testing)
- Later you can change to **Embed** for iframe

---

### Step 4: Save and Copy Client ID

After saving, Moodle will show you the **Client ID**. Copy it!

Example: `GBx1F4LefiUr7bZ` (you already have this in your .env)

---

### Step 5: Add Tool to a Course

1. Go to any course in your Moodle
2. Turn editing ON
3. Click **Add an activity or resource**
4. Select **External tool**
5. Choose **CEPRUD AI Chatbot** from the preconfigured tools
6. Give it a name (e.g., "AI Assistant")
7. Save

---

## 🧪 What to Expect When Testing

### ✅ **Step 1: Click the Tool**
- You'll see a redirect to the chatbot's `/lti/login` endpoint
- Should redirect back to Moodle for authentication

### ✅ **Step 2: Moodle Authentication**
- Moodle will authenticate you
- Generate a JWT with your user/course data
- POST it to `/lti/launch`

### ⚠️ **Step 3: Launch (Current Behavior)**
You'll see **JSON response** instead of the chat:
```json
{
  "success": true,
  "session_id": "lti_session_user123_course_456",
  "user_id": "your_moodle_user_id",
  "email": "your@email.com",
  "name": "Your Name",
  "context_id": "course_id",
  "context_label": "COURSE-CODE",
  "message": "LTI launch successful (demo)"
}
```

**This is EXPECTED!** It proves:
- ✅ OIDC flow works
- ✅ JWT is received and parsed
- ✅ User/course data extracted
- ❌ But chat UI not shown yet

---

## 🔍 Debugging: What to Check

### 1. **Check JWKS Endpoint**
```bash
curl http://150.214.22.87:8080/lti/jwks
```
Should return valid JSON with public keys.

### 2. **Check Server Logs**
```bash
tail -f /tmp/lti_server.log
```
Look for:
- ✅ "Redirecting to OIDC: ..."
- ✅ "LTI launch successful"
- ❌ Any errors or tracebacks

### 3. **Check Moodle Logs**
In Moodle: **Site administration → Reports → Logs**
Look for LTI-related errors.

---

## 📊 Current Implementation Status

| Component | Status | Can Test? |
|-----------|--------|-----------|
| JWKS Endpoint | ✅ Complete | ✅ Yes |
| OIDC Login | ✅ Complete | ✅ Yes |
| JWT Parsing | ✅ Complete | ✅ Yes |
| User Data Extraction | ✅ Complete | ✅ Yes (see JSON) |
| **JWT Signature Verification** | ❌ Not Done | ❌ No |
| **User Auto-Creation** | ❌ Not Done | ❌ No |
| **Session Persistence** | ❌ Not Done | ❌ No |
| **Frontend Integration** | ❌ Not Done | ❌ No |
| **Embedded Chat UI** | ❌ Not Done | ❌ No |

---

## 🎯 Recommendation

### **For a Quick Test (Right Now):**

**YES, you can test the registration**, but expect to see JSON instead of the chat.

**What you'll verify:**
- ✅ Moodle can reach your endpoints
- ✅ OIDC flow works
- ✅ JWT is sent and parsed correctly
- ✅ User/course data is extracted

### **For a Complete Test (After Phase 3):**

Wait for Phase 3 to complete, which adds:
- JWT signature verification
- User auto-login
- Session creation
- Frontend redirect to chat
- Embedded mode

---

## ⏱️ Time Estimate

**Phase 3 implementation:** ~1-2 hours  
**Testing after Phase 3:** Fully functional LTI launch with chat UI

---

## 🤔 My Recommendation

**Option A: Test Registration Now** (15 minutes)
- Register the tool in Moodle
- Verify endpoints are accessible
- See the JSON response
- Then continue to Phase 3

**Option B: Wait for Phase 3** (Recommended)
- Complete Phase 3 first
- Test the full working integration
- Better user experience

---

**What would you like to do?**

1. ✅ **Test registration in Moodle now** (I can help debug)
2. 🚀 **Continue to Phase 3 first** (Complete the integration)
3. ❓ **Ask more questions** about the implementation

Let me know! 😊
