"""
Migration script to import existing CSV logs into MongoDB.
This script reads CSV files and creates MongoDB documents.
"""
import asyncio
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from app.core.database import MongoDB
from app.core.config import settings
from app.models import ConversationMessage, ConversationDocument

logger = logging.getLogger(__name__)


async def migrate_conversations_csv():
    """
    Migrate conversations.csv to MongoDB conversations collection.
    Groups messages by session_id.
    """
    csv_path = Path(settings.BASE_LOG_DIR) / "conversations.csv"
    
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return
    
    logger.info(f"Reading conversations from {csv_path}")
    
    # Read CSV and group by session_id
    sessions: Dict[str, Dict[str, Any]] = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session_id = row['session_id']
            
            # Initialize session if not exists
            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'user_id': row['user_id'],
                    'subject': row['subject'],
                    'messages': []
                }
            
            # Parse timestamp
            timestamp = datetime.fromtimestamp(float(row['timestamp']))
            
            # Clean message content (remove CSV escaping)
            content = row['message_content'].strip('"').replace('""', '"').replace('\\n', '\n').replace('\\r', '\r')
            
            # Add message
            message = ConversationMessage(
                message_type=row['message_type'],
                content=content,
                timestamp=timestamp
            )
            sessions[session_id]['messages'].append(message)
    
    logger.info(f"Found {len(sessions)} sessions with conversations")
    
    # Connect to MongoDB
    await MongoDB.connect()
    collection = MongoDB.get_collection("conversations")
    
    # Insert conversations
    migrated = 0
    for session_id, session_data in sessions.items():
        try:
            # Sort messages by timestamp
            session_data['messages'].sort(key=lambda m: m.timestamp)
            
            # Create conversation document
            conversation = ConversationDocument(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                subject=session_data['subject'],
                messages=session_data['messages'],
                created_at=session_data['messages'][0].timestamp if session_data['messages'] else datetime.utcnow(),
                updated_at=session_data['messages'][-1].timestamp if session_data['messages'] else datetime.utcnow()
            )
            
            # Check if already exists
            existing = await collection.find_one({"session_id": session_id})
            if existing:
                logger.debug(f"Session {session_id} already exists, skipping")
                continue
            
            # Insert document
            await collection.insert_one(conversation.model_dump())
            migrated += 1
            
            if migrated % 100 == 0:
                logger.info(f"Migrated {migrated} conversations...")
                
        except Exception as e:
            logger.error(f"Error migrating session {session_id}: {e}")
    
    logger.info(f"✅ Migration completed! Migrated {migrated} conversations")
    await MongoDB.close()


async def migrate_chat_interactions_csv():
    """
    Migrate chat_interactions_enhanced.csv to MongoDB interaction_analytics collection.
    """
    csv_path = Path(settings.BASE_LOG_DIR) / "chat_interactions_enhanced.csv"
    
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return
    
    logger.info(f"Reading interaction analytics from {csv_path}")
    
    await MongoDB.connect()
    collection = MongoDB.get_collection("interaction_analytics")
    
    migrated = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                timestamp = datetime.fromtimestamp(float(row['timestamp']))
                
                document = {
                    'session_id': row['session_id'],
                    'user_id_partial': row['user_id_partial'],
                    'subject': row['subject'],
                    'message_length': int(row['message_length']),
                    'query_type': row['query_type'],
                    'complexity': row['complexity'],
                    'response_length': int(row['response_length']),
                    'source_count': int(row['source_count']),
                    'llm_model_used': row['model_used'],
                    'timestamp': timestamp
                }
                
                await collection.insert_one(document)
                migrated += 1
                
                if migrated % 100 == 0:
                    logger.info(f"Migrated {migrated} interaction records...")
                    
            except Exception as e:
                logger.error(f"Error migrating interaction record: {e}")
    
    logger.info(f"✅ Migration completed! Migrated {migrated} interaction records")
    await MongoDB.close()


async def migrate_session_events_csv():
    """
    Migrate learning_sessions.csv to MongoDB session_events collection.
    """
    csv_path = Path(settings.BASE_LOG_DIR) / "learning_sessions.csv"
    
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return
    
    logger.info(f"Reading session events from {csv_path}")
    
    await MongoDB.connect()
    collection = MongoDB.get_collection("session_events")
    
    migrated = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                timestamp = datetime.fromtimestamp(float(row['timestamp']))
                
                document = {
                    'session_id': row['session_id'],
                    'user_id': row['user_id'],
                    'subject': row['subject'],
                    'event_type': row['event_type'],
                    'timestamp': timestamp
                }
                
                await collection.insert_one(document)
                migrated += 1
                
                if migrated % 100 == 0:
                    logger.info(f"Migrated {migrated} session events...")
                    
            except Exception as e:
                logger.error(f"Error migrating session event: {e}")
    
    logger.info(f"✅ Migration completed! Migrated {migrated} session events")
    await MongoDB.close()


async def migrate_learning_events_csv():
    """
    Migrate learning_events.csv to MongoDB learning_events collection.
    """
    csv_path = Path(settings.BASE_LOG_DIR) / "learning_events.csv"
    
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return
    
    logger.info(f"Reading learning events from {csv_path}")
    
    await MongoDB.connect()
    collection = MongoDB.get_collection("learning_events")
    
    migrated = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                timestamp = datetime.fromtimestamp(float(row['timestamp']))
                
                document = {
                    'session_id': row['session_id'],
                    'event_type': row['event_type'],
                    'topic': row['topic'],
                    'confidence_level': row['confidence_level'],
                    'timestamp': timestamp
                }
                
                await collection.insert_one(document)
                migrated += 1
                
                if migrated % 100 == 0:
                    logger.info(f"Migrated {migrated} learning events...")
                    
            except Exception as e:
                logger.error(f"Error migrating learning event: {e}")
    
    logger.info(f"✅ Migration completed! Migrated {migrated} learning events")
    await MongoDB.close()


async def run_full_migration():
    """Run complete migration from CSV to MongoDB"""
    logger.info("🚀 Starting full migration from CSV to MongoDB")
    
    try:
        await migrate_conversations_csv()
        await migrate_chat_interactions_csv()
        await migrate_session_events_csv()
        await migrate_learning_events_csv()
        
        logger.info("🎉 All migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_full_migration())
