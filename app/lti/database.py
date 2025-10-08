"""
Database connection for LTI services

Provides MongoDB connection for LTI user and session management.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client (singleton)
_mongo_client: AsyncIOMotorClient = None
_database: AsyncIOMotorDatabase = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        logger.info(f"Connecting to MongoDB: {mongo_uri}")
        _mongo_client = AsyncIOMotorClient(mongo_uri)
    return _mongo_client


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance for LTI data"""
    global _database
    if _database is None:
        client = get_mongo_client()
        database_name = os.getenv("MONGODB_DATABASE", "chatbot_users")
        _database = client[database_name]
        logger.info(f"Using database: {database_name}")
    return _database


async def close_mongo_connection():
    """Close MongoDB connection (call on app shutdown)"""
    global _mongo_client, _database
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _database = None
        logger.info("MongoDB connection closed")
