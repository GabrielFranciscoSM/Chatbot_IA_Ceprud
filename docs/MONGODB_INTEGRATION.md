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

### Main Application API (Port 8080)
- `POST /user/create` - Create new user account
- `POST /user/login` - Simple email-based login
- `POST /user/logout` - Logout endpoint
- `GET /user/profile?email={email}` - Get user profile
- `PUT /user/profile?email={email}` - Update user profile

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
