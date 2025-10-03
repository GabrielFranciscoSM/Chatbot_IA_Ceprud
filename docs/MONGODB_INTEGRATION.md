# MongoDB User Service Integration

This document describes the new MongoDB user service that has been added to your chatbot project.

## Overview

The MongoDB service provides a simple and scalable way to store and manage user data for your chatbot application. It consists of:

1. **MongoDB Database** - Stores user data
2. **User Service API** - FastAPI service for user CRUD operations  
3. **User Service Client** - HTTP client for integration with your main app
4. **User Management Endpoints** - API endpoints in your main application

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Backend       │───▶│   User Service  │
│   (Port 8090)   │    │   (Port 8080)   │    │   (Port 8083)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   MongoDB       │
                                               │   (Port 27017)  │
                                               └─────────────────┘
```

## What's Been Added

### 1. MongoDB Service (`mongo-service/`)
- **Dockerfile** - Container configuration
- **requirements.txt** - Python dependencies
- **app/main.py** - FastAPI application with user CRUD endpoints
- **app/models.py** - Pydantic models for user data
- **app/database.py** - Database connection utilities

### 2. Docker Configuration Updates
- Added MongoDB container to `docker-compose-full.yml`
- Added User Service container 
- Added persistent volume for MongoDB data
- Updated environment variables for service communication

### 3. Main Application Integration
- **app/services/user_service.py** - HTTP client for user service
- **app/core/models.py** - Added user-related request/response models
- **app/api_router.py** - Added user management endpoints

### 4. Testing and Documentation
- **test_user_service.py** - Test script for validation
- **mongo-service/README.md** - Service documentation

## User Data Model

Each user has the following fields:

```python
{
    "id": "string",           # Auto-generated MongoDB ObjectId
    "email": "string",        # Unique email address
    "name": "string",         # Full name
    "role": "string",         # User role (student/teacher/admin)
    "active": boolean,        # Account status
    "subjects": ["string"],   # List of subject IDs associated with user
    "created_at": "datetime", # Creation timestamp
    "updated_at": "datetime"  # Last update timestamp
}
```

## API Endpoints

### Direct User Service API (Port 8083)
- `GET /health` - Health check
- `POST /users` - Create user
- `GET /users/{user_id}` - Get user by ID
- `GET /users/email/{email}` - Get user by email
- `GET /users` - List users (paginated)
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

**Subject Management (User Service):**
- `GET /users/{user_id}/subjects` - Get user subjects by ID
- `GET /users/email/{email}/subjects` - Get user subjects by email
- `POST /users/{user_id}/subjects` - Add subject to user by ID
- `POST /users/email/{email}/subjects` - Add subject to user by email
- `DELETE /users/{user_id}/subjects/{subject_id}` - Remove subject by ID
- `DELETE /users/email/{email}/subjects/{subject_id}` - Remove subject by email

### Main Application API (Port 8080)
- `POST /user/create` - Create new user account
- `POST /user/login` - Simple email-based login
- `POST /user/logout` - Logout endpoint
- `GET /user/profile?email={email}` - Get user profile
- `PUT /user/profile?email={email}` - Update user profile

**Subject Management (Main API):**
- `GET /user/subjects?email={email}` - Get user's subjects
- `POST /user/subjects` - Add subject to user
- `DELETE /user/subjects/{subject_id}?email={email}` - Remove subject from user

## How to Use

### 1. Start Services
```bash
docker-compose -f docker-compose-full.yml up mongodb user-service backend
```

### 2. Test the Service
```bash
python test_user_service.py
```

### 3. Create a User (via main app)
```python
import httpx

async def create_user():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8080/user/create", json={
            "email": "student@university.edu",
            "name": "John Doe",
            "role": "student"
        })
        return response.json()
```

### 4. Use in Your Code
```python
from services.user_service import user_service

# Create user
user = await user_service.create_user("user@email.com", "User Name")

# Get user
user = await user_service.get_user_by_email("user@email.com")

# Update user
updated = await user_service.update_user(user_id, name="New Name")

# Subject management
subjects = await user_service.get_user_subjects("user@email.com")
await user_service.add_subject_to_user("user@email.com", "ingenieria_de_servidores")
await user_service.remove_subject_from_user("user@email.com", "metaheuristicas")
```

## Subject Management Feature

### Overview
Each user can have an associated list of subjects (courses). This allows personalized subject selection and access control.

### How It Works

1. **Frontend Search & Add**
   - User searches for available subjects using a search bar
   - Clicks on a subject to add it to their list
   - Subject appears in their sidebar

2. **Backend Processing**
   - Frontend calls `/user/subjects` endpoint
   - Backend proxies to User Service
   - MongoDB updates user's subjects array

3. **Subject Display**
   - Only user's subjects are shown in the sidebar
   - Empty state shown if no subjects added
   - Hover to see remove button (×)

### API Examples

**Add a subject:**
```bash
curl -X POST http://localhost:8080/user/subjects \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@correo.ugr.es",
    "subject_id": "ingenieria_de_servidores"
  }'
```

**Remove a subject:**
```bash
curl -X DELETE "http://localhost:8080/user/subjects/ingenieria_de_servidores?email=user@correo.ugr.es"
```

**Get user subjects:**
```bash
curl "http://localhost:8080/user/subjects?email=user@correo.ugr.es"
```

### Database Operations

The subjects are stored as an array in the user document:

```javascript
// MongoDB update to add subject
db.users.updateOne(
  { email: "user@correo.ugr.es" },
  { 
    $push: { subjects: "ingenieria_de_servidores" },
    $set: { updated_at: new Date() }
  }
)

// MongoDB update to remove subject
db.users.updateOne(
  { email: "user@correo.ugr.es" },
  { 
    $pull: { subjects: "ingenieria_de_servidores" },
    $set: { updated_at: new Date() }
  }
)
```

## Environment Variables

The following environment variables are configured automatically in docker-compose:

- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DATABASE` - Database name (default: `chatbot_users`)
- `USER_SERVICE_URL` - User service URL for the main app

## Security Considerations

This is a simple implementation. For production use, consider adding:

- Authentication and authorization
- Input validation and sanitization
- Rate limiting
- Database connection pooling
- Logging and monitoring
- Backup strategies
- SSL/TLS encryption

## Next Steps

Now that you have a user service, you can:

1. **Integrate with Chat Sessions** - Link user data to chat sessions
2. **Add User Preferences** - Store user settings and preferences
3. **Implement Analytics** - Track user interactions and behavior
4. **Add Authentication** - Implement proper login/logout with JWT tokens
5. **Extend User Model** - Add more fields as needed (avatar, preferences, etc.)

The service is designed to be simple and extensible, so you can easily add more features as your chatbot evolves.
