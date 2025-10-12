"""
MongoDB index creation for optimizing queries.
Run this script to create indexes on collections.
"""
import asyncio
import logging
from app.core.database import MongoDB
from app.core.config import settings

logger = logging.getLogger(__name__)


async def create_indexes():
    """Create MongoDB indexes for all collections"""
    try:
        await MongoDB.connect()
        
        # Conversations collection indexes
        conversations = MongoDB.get_collection("conversations")
        await conversations.create_index("session_id", unique=True)
        await conversations.create_index("user_id")
        await conversations.create_index("subject")
        await conversations.create_index([("created_at", -1)])
        await conversations.create_index([("updated_at", -1)])
        logger.info("✓ Indexes created for 'conversations' collection")
        
        # Session events collection indexes
        session_events = MongoDB.get_collection("session_events")
        await session_events.create_index("session_id")
        await session_events.create_index("user_id")
        await session_events.create_index("subject")
        await session_events.create_index([("timestamp", -1)])
        await session_events.create_index([("event_type", 1), ("timestamp", -1)])
        logger.info("✓ Indexes created for 'session_events' collection")
        
        # Interaction analytics collection indexes
        interaction_analytics = MongoDB.get_collection("interaction_analytics")
        await interaction_analytics.create_index("session_id")
        await interaction_analytics.create_index("user_id_partial")
        await interaction_analytics.create_index("subject")
        await interaction_analytics.create_index([("timestamp", -1)])
        await interaction_analytics.create_index([("query_type", 1), ("timestamp", -1)])
        await interaction_analytics.create_index([("complexity", 1), ("timestamp", -1)])
        logger.info("✓ Indexes created for 'interaction_analytics' collection")
        
        # Learning events collection indexes
        learning_events = MongoDB.get_collection("learning_events")
        await learning_events.create_index("session_id")
        await learning_events.create_index("event_type")
        await learning_events.create_index("topic")
        await learning_events.create_index([("timestamp", -1)])
        logger.info("✓ Indexes created for 'learning_events' collection")
        
        logger.info("🎉 All indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_indexes())
