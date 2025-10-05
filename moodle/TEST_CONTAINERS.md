# 🐳 Container Testing - Phase 4 LTI Integration

## ✅ All Containers Running

```
chatbot-frontend         Up 29 minutes  0.0.0.0:8090->8090/tcp
chatbot-backend          Up 29 minutes  0.0.0.0:8080->8080/tcp
chatbot-user-service     Up 29 minutes  0.0.0.0:8083->8083/tcp
chatbot-rag-service      Up 29 minutes  0.0.0.0:8082->8082/tcp
chatbot-logging-service  Up 29 minutes  0.0.0.0:8002->8002/tcp
chatbot-mongo-express    Up 29 minutes  0.0.0.0:8081->8081/tcp
chatbot-mongodb          Up 29 minutes  0.0.0.0:27017->27017/tcp
```

## 🚀 Test URL for LTI Mode

**IMPORTANT**: Frontend is now on port **8090** (not 3000)

```
http://localhost:8090/?session_token=TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg&lti=true&subject=ingenieria_de_servidores
```

⚠️ **NOTE**: The backend container may need a full rebuild to include the latest `/session/validate` endpoint. If you see validation errors, rebuild with:

```bash
# Touch the file to force rebuild
touch app/api_router.py

# Rebuild backend without cache
podman-compose -f docker-compose-full.yml stop backend
podman-compose -f docker-compose-full.yml rm -f backend  
podman-compose -f docker-compose-full.yml build --no-cache backend
podman-compose -f docker-compose-full.yml up -d backend
```

## 🔑 Test Session Details

- **Token**: `TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg`
- **User**: test@ugr.es (Test User LTI)
- **Subject**: ingenieria_de_servidores
- **Course**: IS-2025-TEST
- **Expires**: 2025-10-05 23:41:53 UTC

## ✅ Expected Behavior

1. **Loading** - Brief spinner
2. **Session validates** - Backend calls MongoDB
3. **LTI Mode UI**:
   - ❌ **No sidebar** (hidden)
   - 📊 **Context banner** shows "IS-2025-TEST"
   - 👤 **Auto-login** as test@ugr.es
   - 📚 **Subject selected**: ingenieria_de_servidores
   - 💬 **Chat ready**

## 🔍 Quick Verification

### 1. Health Check
```bash
curl http://localhost:8080/health
```
Expected: `{"status":"healthy",...}`

### 2. Session Validation (manual test)
```bash
curl -H "X-Session-Token: TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg" \
     http://localhost:8080/session/validate
```
Expected: User data with email, name, subject, context_label

### 3. Browser Test
Open the test URL above and check:
- DevTools Console: No errors
- Network Tab → `/session/validate`: 200 OK
- Visual: No sidebar, banner shows "IS-2025-TEST"

## 🐛 If Session Expired

The test session expires at **23:41:53 UTC (2025-10-05)**.

If you see "Session expired" or validation fails:

```bash
# Stop local npm dev server if running
# (Containers are already using the ports)

# Recreate test session
.venv/bin/python moodle/create_test_session.py

# Use the new token from the output
```

## 🌐 Service URLs

- **Frontend**: http://localhost:8090
- **Backend API**: http://localhost:8080
- **Mongo Express**: http://localhost:8081 (admin/password123)
- **User Service**: http://localhost:8083
- **RAG Service**: http://localhost:8082
- **Logging Service**: http://localhost:8002

## 🎯 Container Advantages

✅ **Real production setup** - Exact same as deployment  
✅ **Network configured** - Services can talk to each other  
✅ **No proxy errors** - Everything in Docker network  
✅ **Database shared** - All services use same MongoDB  
✅ **Isolated** - No conflicts with local dev servers  

## 📝 Container Management

### View Logs
```bash
# All containers
podman-compose -f docker-compose-full.yml logs -f

# Specific service
podman logs -f chatbot-backend
podman logs -f chatbot-frontend
```

### Restart After Code Changes
```bash
# Rebuild and restart specific service
podman-compose -f docker-compose-full.yml build backend
podman-compose -f docker-compose-full.yml up -d backend

# Or rebuild all
podman-compose -f docker-compose-full.yml build
podman-compose -f docker-compose-full.yml up -d
```

### Stop All
```bash
podman-compose -f docker-compose-full.yml down
```

### Stop and Remove Volumes (fresh start)
```bash
podman-compose -f docker-compose-full.yml down -v
```

## 🎉 Ready to Test!

**Open this URL now:**
```
http://localhost:8090/?session_token=TEST_SESSION_dKz5MPg4Yb3-Phu-PgW-Jg&lti=true&subject=ingenieria_de_servidores
```

You should see the chatbot in **LTI mode** ready for use! 🚀
