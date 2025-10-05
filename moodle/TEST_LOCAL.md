# 🧪 Local Testing Guide - Phase 4 LTI Integration

## ✅ Services Status

- **MongoDB**: Running on port 27017 (Podman container)
- **Backend**: Running on port 8080 (FastAPI)
- **Frontend**: Running on port 3000 (Vite)

## 🔑 Test Session Details

**Session Token**: `TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg`  
**User**: test@ugr.es (Test User LTI)  
**Subject**: ingenieria_de_servidores  
**Course**: IS-2025-TEST  
**Expires**: 2025-10-05 23:41:53 UTC (8 hours)

## 🚀 Test URL

Open this URL in your browser to test LTI mode:

```
http://localhost:3000/?session_token=TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg&lti=true&subject=ingenieria_de_servidores
```

## ✅ Expected Behavior

1. **Initial Load**:
   - ⏳ Loading spinner appears briefly
   - 🔄 Frontend calls `/session/validate` with session token
   - ✅ Backend validates session from MongoDB

2. **UI Changes (LTI Mode)**:
   - ❌ Sidebar is **hidden** (no subject selector)
   - 📊 Context banner shows **"IS-2025-TEST"**
   - 👤 User auto-logged in as **test@ugr.es**
   - 📚 Subject pre-selected: **ingenieria_de_servidores**
   - 💬 Chat interface ready to use

3. **API Calls**:
   - All requests include `X-Session-Token` header
   - Session validated before any chat interaction

## 🔍 Verification Checklist

### Browser DevTools Console
- [ ] No errors related to session validation
- [ ] Log: "Session validated successfully" or similar
- [ ] User object logged with email, name, role

### Network Tab → `/session/validate` Request
- [ ] Status: **200 OK**
- [ ] Request headers include `X-Session-Token`
- [ ] Response includes:
  ```json
  {
    "user": {
      "id": "68e29175cee569f7989364ce",
      "name": "Test User LTI",
      "email": "test@ugr.es",
      "role": "Learner"
    },
    "subject": "ingenieria_de_servidores",
    "context_label": "IS-2025-TEST",
    "lti_user_id": "test_lti_user_123"
  }
  ```

### Visual Inspection
- [ ] No sidebar visible on left
- [ ] Top banner shows "IS-2025-TEST"
- [ ] Chat input is enabled
- [ ] User name "Test User LTI" visible somewhere in UI

### Send Test Message
- [ ] Type: "Hola, ¿qué es un servidor?"
- [ ] Click Send
- [ ] Check Network tab → `/chat` request
- [ ] Verify `X-Session-Token` header present
- [ ] Response should include chatbot answer

## 🐛 Troubleshooting

### Issue: Session Validation Fails (401/403)
**Check**:
1. MongoDB connection: `podman ps | grep mongodb`
2. Session in database: Session expires at 23:41:53 UTC
3. Backend logs for authentication errors
4. Token matches exactly (no extra spaces)

**Solution**:
```bash
# Recreate test session
cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud
.venv/bin/python moodle/create_test_session.py
```

### Issue: UI Shows Sidebar (Not in LTI Mode)
**Check**:
1. URL includes `lti=true` parameter
2. SessionContext parsed URL correctly
3. Browser console for `session.isLTI` value

**Debug**:
```javascript
// In browser console
localStorage.getItem('sessionToken')
// Should show: TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg
```

### Issue: Network Errors (CORS)
**Check**:
1. Backend CORS allows `http://localhost:3000`
2. `X-Session-Token` in exposed headers
3. Frontend using correct backend URL

**Backend CORS Config** (app/app.py):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ...],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)
```

### Issue: Session Expired
**Error**: Session validation returns 401 with "Session expired"

**Solution**:
```bash
# Create new test session
.venv/bin/python moodle/create_test_session.py
# Use new token from output
```

## 📊 MongoDB Verification

To manually check the session in MongoDB:

```bash
# Connect to MongoDB
podman exec -it chatbot-mongodb mongosh -u admin -p password123

# Switch to database
use chatbot_users

# Find session
db.lti_sessions.findOne({
  session_token: "TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg"
})

# Expected output:
{
  _id: ObjectId("68e291c115131661509ed212"),
  session_token: "TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg",
  user_id: "68e29175cee569f7989364ce",
  lti_user_id: "test_lti_user_123",
  context_id: "test_course_456",
  context_label: "IS-2025-TEST",
  subject: "ingenieria_de_servidores",
  created_at: ISODate("..."),
  expires_at: ISODate("2025-10-05T23:41:53.014Z")
}
```

## 🎯 Success Criteria

Phase 4 local testing is successful when:

1. ✅ Session validates on page load
2. ✅ UI switches to LTI mode (no sidebar)
3. ✅ Context banner displays course name
4. ✅ User auto-logged in
5. ✅ Subject pre-selected
6. ✅ Chat messages work with session token headers
7. ✅ No console errors
8. ✅ Clean user experience suitable for iframe embedding

## 📝 Next Steps After Successful Test

1. **Moodle Cloud Registration**:
   - Register tool at testchatbot.moodlecloud.com
   - Configure with production URL (not localhost)
   - Test real LTI launch from Moodle

2. **Deployment**:
   - Deploy backend with public URL
   - Update JWKS endpoint URL
   - Configure SSL/TLS certificates
   - Update Moodle tool configuration

3. **Production Testing**:
   - Create test course in Moodle
   - Add chatbot as external tool
   - Launch from Moodle and verify session flow
   - Test different user roles (Student, Teacher)

## 📚 Related Documentation

- [Phase 4 Complete Guide](./PHASE_4_COMPLETE.md)
- [Phase 4 Summary](./PHASE_4_SUMMARY.md)
- [Moodle Testing Guide](./TESTING_IN_MOODLE_NOW.md)
- [API Documentation](../docs/API.md)

---

**Last Updated**: 2025-10-05  
**Session Expires**: 2025-10-05 23:41:53 UTC
