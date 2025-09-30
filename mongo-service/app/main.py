from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from typing import List, Optional
from .models import User, UserCreate, UserUpdate
from .database import get_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection lifecycle"""
    global mongodb_client
    
    # Startup
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    mongodb_client = AsyncIOMotorClient(mongodb_url)
    
    try:
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    
    yield
    
    # Shutdown
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


app = FastAPI(
    title="User Data Service",
    description="Simple MongoDB service for storing user data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-data-service"}


@app.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        db = get_database(mongodb_client)
        collection = db.users
        
        # Check if user already exists
        existing_user = await collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create user document with timestamps
        from datetime import datetime
        user_dict = user_data.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        result = await collection.insert_one(user_dict)
        
        # Return created user
        created_user = await collection.find_one({"_id": result.inserted_id})
        created_user["id"] = str(created_user["_id"])
        del created_user["_id"]
        
        logger.info(f"Created user: {user_data.email}")
        return User(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        from bson import ObjectId
        db = get_database(mongodb_client)
        collection = db.users
        
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["id"] = str(user["_id"])
        del user["_id"]
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """Get list of users with pagination"""
    try:
        db = get_database(mongodb_client)
        collection = db.users
        
        cursor = collection.find().skip(skip).limit(limit)
        users = []
        
        async for user in cursor:
            user["id"] = str(user["_id"])
            del user["_id"]
            users.append(User(**user))
        
        return users
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """Get user by email"""
    try:
        db = get_database(mongodb_client)
        collection = db.users
        
        user = await collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["id"] = str(user["_id"])
        del user["_id"]
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user by ID"""
    try:
        from bson import ObjectId
        db = get_database(mongodb_client)
        collection = db.users
        
        # Only update fields that are provided
        update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Add updated timestamp
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return updated user
        updated_user = await collection.find_one({"_id": ObjectId(user_id)})
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]
        
        logger.info(f"Updated user: {user_id}")
        return User(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user by ID"""
    try:
        from bson import ObjectId
        db = get_database(mongodb_client)
        collection = db.users
        
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Deleted user: {user_id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
