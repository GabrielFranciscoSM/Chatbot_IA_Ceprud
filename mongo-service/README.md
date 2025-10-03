# MongoDB User Service

A simple FastAPI service for managing user data using MongoDB.

## Features

- Create, read, update, and delete user records
- Simple email-based user identification
- RESTful API endpoints
- Async MongoDB operations using Motor
- Health check endpoint
- Docker containerized

## API Endpoints

### Health Check
- **GET** `/health` - Check service health

### User Management
- **POST** `/users` - Create a new user
- **GET** `/users/{user_id}` - Get user by ID  
- **GET** `/users/email/{email}` - Get user by email
- **GET** `/users` - Get all users (with pagination)
- **PUT** `/users/{user_id}` - Update user
- **DELETE** `/users/{user_id}` - Delete user

## User Model

```json
{
  "id": "string",
  "email": "user@example.com",
  "name": "User Name",
  "role": "student",
  "active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

## Environment Variables

- `MONGODB_URL` - MongoDB connection string (default: `mongodb://mongodb:27017`)
- `MONGODB_DATABASE` - Database name (default: `chatbot_users`)

## Usage

The service is automatically started with docker-compose:

```bash
docker-compose up user-service
```

## Integration

The main chatbot application includes a `UserServiceClient` in `app/services/user_service.py` for easy integration:

```python
from services.user_service import user_service

# Create user
user = await user_service.create_user("user@email.com", "User Name")

# Get user
user = await user_service.get_user_by_email("user@email.com")
```

## API Endpoints in Main App

The main application exposes user management through these endpoints:

- **POST** `/user/create` - Create new user account
- **POST** `/user/login` - Simple email-based login
- **POST** `/user/logout` - Logout endpoint
- **GET** `/user/profile?email=user@email.com` - Get user profile
- **PUT** `/user/profile?email=user@email.com` - Update user profile
