from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import os


def get_database(client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Get database instance"""
    database_name = os.getenv("MONGODB_DATABASE", "chatbot_users")
    return client[database_name]
