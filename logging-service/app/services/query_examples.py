"""
Example script to query conversations from MongoDB.
Demonstrates how to use the MongoDB collections for analytics.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from app.core.database import MongoDB
from app.core.config import settings

logger = logging.getLogger(__name__)


async def example_queries():
    """Run example queries on the conversations database"""
    try:
        await MongoDB.connect()
        
        # Example 1: Get all conversations for a specific session
        print("\n📝 Example 1: Get conversation by session ID")
        conversations = MongoDB.get_collection("conversations")
        session_conv = await conversations.find_one({"session_id": "example-session-123"})
        if session_conv:
            print(f"  Session: {session_conv['session_id']}")
            print(f"  User: {session_conv['user_id']}")
            print(f"  Subject: {session_conv['subject']}")
            print(f"  Messages: {len(session_conv['messages'])}")
        else:
            print("  No conversation found for this session")
        
        # Example 2: Get all conversations for a user
        print("\n👤 Example 2: Get all conversations for a user")
        user_id = "test@example.com"
        cursor = conversations.find({"user_id": user_id}).sort("created_at", -1)
        count = 0
        async for conv in cursor:
            count += 1
            print(f"  - Session {conv['session_id']}: {len(conv['messages'])} messages in {conv['subject']}")
        print(f"  Total conversations: {count}")
        
        # Example 3: Get conversations by subject
        print("\n📚 Example 3: Get conversations by subject")
        subject = "Cálculo I"
        cursor = conversations.find({"subject": subject}).sort("created_at", -1).limit(5)
        count = 0
        async for conv in cursor:
            count += 1
            print(f"  - Session {conv['session_id']}: {conv['user_id']} - {len(conv['messages'])} messages")
        print(f"  Total conversations (limited to 5): {count}")
        
        # Example 4: Get recent conversations (last 7 days)
        print("\n🕐 Example 4: Get recent conversations (last 7 days)")
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        cursor = conversations.find({
            "created_at": {"$gte": seven_days_ago}
        }).sort("created_at", -1)
        count = 0
        async for conv in cursor:
            count += 1
            print(f"  - {conv['created_at'].strftime('%Y-%m-%d %H:%M')}: {conv['subject']} ({len(conv['messages'])} messages)")
        print(f"  Total recent conversations: {count}")
        
        # Example 5: Aggregate statistics
        print("\n📊 Example 5: Conversation statistics")
        pipeline = [
            {
                "$group": {
                    "_id": "$subject",
                    "total_conversations": {"$sum": 1},
                    "total_messages": {"$sum": {"$size": "$messages"}},
                    "avg_messages_per_conv": {"$avg": {"$size": "$messages"}}
                }
            },
            {"$sort": {"total_conversations": -1}}
        ]
        async for result in conversations.aggregate(pipeline):
            print(f"  Subject: {result['_id']}")
            print(f"    - Total conversations: {result['total_conversations']}")
            print(f"    - Total messages: {result['total_messages']}")
            print(f"    - Avg messages per conversation: {result['avg_messages_per_conv']:.2f}")
        
        # Example 6: Find conversations with specific keywords
        print("\n🔍 Example 6: Search conversations by content")
        keyword = "derivada"
        cursor = conversations.find({
            "messages.content": {"$regex": keyword, "$options": "i"}
        })
        count = 0
        async for conv in cursor:
            count += 1
            # Find messages containing the keyword
            matching_messages = [m for m in conv['messages'] if keyword.lower() in m['content'].lower()]
            print(f"  - Session {conv['session_id']}: {len(matching_messages)} messages match '{keyword}'")
        print(f"  Total conversations with keyword: {count}")
        
        # Example 7: Get analytics data
        print("\n📈 Example 7: Interaction analytics")
        analytics = MongoDB.get_collection("interaction_analytics")
        pipeline = [
            {
                "$group": {
                    "_id": "$query_type",
                    "count": {"$sum": 1},
                    "avg_message_length": {"$avg": "$message_length"},
                    "avg_response_length": {"$avg": "$response_length"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        async for result in analytics.aggregate(pipeline):
            print(f"  Query Type: {result['_id']}")
            print(f"    - Count: {result['count']}")
            print(f"    - Avg message length: {result['avg_message_length']:.2f}")
            print(f"    - Avg response length: {result['avg_response_length']:.2f}")
        
        print("\n✅ Query examples completed!")
        
    except Exception as e:
        logger.error(f"Error running queries: {e}")
        raise
    finally:
        await MongoDB.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(example_queries())
