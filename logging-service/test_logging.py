"""
Simple test script to verify MongoDB logging functionality.
Run this after the logging service is up.
"""
import asyncio
import httpx
import time
from datetime import datetime

LOGGING_SERVICE_URL = "http://localhost:8002"


async def test_logging_service():
    """Test the logging service endpoints"""
    
    print("🧪 Testing Logging Service with MongoDB\n")
    
    # Test session ID
    session_id = f"test-session-{int(time.time())}"
    user_id = "test-user@example.com"
    subject = "Test Subject"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # 1. Health check
        print("1️⃣ Testing health endpoint...")
        response = await client.get(f"{LOGGING_SERVICE_URL}/health")
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}\n")
        else:
            print(f"   ❌ Health check failed: {response.status_code}\n")
            return
        
        # 2. Log session start event
        print("2️⃣ Testing session event logging...")
        response = await client.post(
            f"{LOGGING_SERVICE_URL}/api/v1/logs/session-event",
            json={
                "session_id": session_id,
                "user_id": user_id,
                "subject": subject,
                "event_type": "session_start"
            }
        )
        if response.status_code == 200:
            print(f"   ✅ Session event logged: {response.json()}\n")
        else:
            print(f"   ❌ Failed to log session event: {response.status_code}\n")
        
        # 3. Log user message (conversation)
        print("3️⃣ Testing conversation message logging (user)...")
        timestamp = time.time()
        response = await client.post(
            f"{LOGGING_SERVICE_URL}/api/v1/logs/conversation-message",
            json={
                "session_id": session_id,
                "user_id": user_id,
                "subject": subject,
                "message_type": "user",
                "message_content": "¿Qué es una derivada?",
                "timestamp": timestamp
            }
        )
        if response.status_code == 200:
            print(f"   ✅ User message logged: {response.json()}\n")
        else:
            print(f"   ❌ Failed to log user message: {response.status_code}\n")
        
        # 4. Log bot response (conversation)
        print("4️⃣ Testing conversation message logging (bot)...")
        timestamp = time.time()
        response = await client.post(
            f"{LOGGING_SERVICE_URL}/api/v1/logs/conversation-message",
            json={
                "session_id": session_id,
                "user_id": user_id,
                "subject": subject,
                "message_type": "bot",
                "message_content": "Una derivada representa la tasa de cambio instantánea de una función...",
                "timestamp": timestamp
            }
        )
        if response.status_code == 200:
            print(f"   ✅ Bot response logged: {response.json()}\n")
        else:
            print(f"   ❌ Failed to log bot response: {response.status_code}\n")
        
        # 5. Log interaction analytics
        print("5️⃣ Testing interaction analytics logging...")
        response = await client.post(
            f"{LOGGING_SERVICE_URL}/api/v1/logs/user-message",
            json={
                "session_id": session_id,
                "user_id_partial": user_id[:8] + "...",
                "subject": subject,
                "message_length": 21,
                "query_type": "conceptual",
                "complexity": "medium",
                "response_length": 150,
                "source_count": 3,
                "llm_model_used": "granite-3.3-2b"
            }
        )
        if response.status_code == 200:
            print(f"   ✅ Analytics logged: {response.json()}\n")
        else:
            print(f"   ❌ Failed to log analytics: {response.status_code}\n")
        
        # 6. Wait a moment for MongoDB to process
        print("⏳ Waiting for MongoDB to process...")
        await asyncio.sleep(2)
        
        # 7. Retrieve the conversation
        print("\n7️⃣ Testing conversation retrieval...")
        response = await client.get(
            f"{LOGGING_SERVICE_URL}/api/v1/conversations/{session_id}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Conversation retrieved successfully!")
            print(f"   📝 Session: {data['session_id']}")
            print(f"   👤 User: {data['user_id']}")
            print(f"   📚 Subject: {data['subject']}")
            print(f"   💬 Messages: {len(data['messages'])}")
            print(f"   📅 Created: {data['created_at']}")
            for i, msg in enumerate(data['messages'], 1):
                print(f"      {i}. [{msg['message_type']}]: {msg['content'][:50]}...")
            print()
        else:
            print(f"   ❌ Failed to retrieve conversation: {response.status_code}")
            print(f"   Response: {response.text}\n")
        
        # 8. Retrieve conversations by user
        print("8️⃣ Testing user conversations retrieval...")
        response = await client.get(
            f"{LOGGING_SERVICE_URL}/api/v1/conversations/user/{user_id}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User conversations retrieved!")
            print(f"   📊 Count: {data['count']}")
            print()
        else:
            print(f"   ❌ Failed to retrieve user conversations: {response.status_code}\n")
        
        # 9. Retrieve analytics
        print("9️⃣ Testing analytics retrieval...")
        response = await client.get(
            f"{LOGGING_SERVICE_URL}/api/v1/analytics/interactions?subject={subject}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analytics retrieved!")
            print(f"   📊 Interaction count: {data['count']}")
            print()
        else:
            print(f"   ❌ Failed to retrieve analytics: {response.status_code}\n")
        
        print("=" * 60)
        print("🎉 All tests completed!")
        print("=" * 60)
        print(f"\nTest session ID: {session_id}")
        print(f"You can view the conversation at:")
        print(f"  {LOGGING_SERVICE_URL}/api/v1/conversations/{session_id}")
        print(f"\nOr in Mongo Express:")
        print(f"  http://localhost:8081")
        print(f"  Database: chatbot_logs")
        print(f"  Collection: conversations")


if __name__ == "__main__":
    try:
        asyncio.run(test_logging_service())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
