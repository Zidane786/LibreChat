"""MongoDB database connection and initialization"""
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.config import get_settings

logger = logging.getLogger(__name__)

# Global database client and instance
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> AsyncIOMotorDatabase:
    """
    Initialize MongoDB connection and Beanie ODM

    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    global _client, _database

    settings = get_settings()

    try:
        logger.info(f"Connecting to MongoDB at {settings.mongo_uri.split('@')[-1] if '@' in settings.mongo_uri else settings.mongo_uri}")

        # Create MongoDB client with connection pool settings
        _client = AsyncIOMotorClient(
            settings.mongo_uri,
            maxPoolSize=settings.mongo_max_pool_size,
            minPoolSize=settings.mongo_min_pool_size,
            maxIdleTimeMS=settings.mongo_max_idle_time_ms,
            waitQueueTimeoutMS=settings.mongo_wait_queue_timeout_ms,
            serverSelectionTimeoutMS=10000,  # 10 seconds timeout for initial connection
        )

        # Get database name from URI or use default
        db_name = settings.mongo_uri.split("/")[-1].split("?")[0] or "librechat"
        _database = _client[db_name]

        # Test connection
        await _client.admin.command("ping")
        logger.info(f"Successfully connected to MongoDB database: {db_name}")

        # Import all models to register them
        from app.models import (
            User, Conversation, Message, File, Preset, Prompt, PromptGroup,
            Agent, Assistant, Action, Role, Transaction, Balance, ToolCall,
            ConversationTag, Project, Banner, Categories
        )

        # Initialize Beanie with all document models
        await init_beanie(
            database=_database,
            document_models=[
                User, Conversation, Message, File, Preset, Prompt, PromptGroup,
                Agent, Assistant, Action, Role, Transaction, Balance, ToolCall,
                ConversationTag, Project, Banner, Categories
            ],
        )

        logger.info("Beanie ODM initialized successfully")

        # Create indexes if auto_index is enabled
        if settings.mongo_auto_index:
            logger.info("Creating database indexes...")
            # Indexes will be created automatically by Beanie based on model definitions

        return _database

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_db():
    """Close MongoDB connection"""
    global _client, _database

    if _client:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get current database instance

    Returns:
        AsyncIOMotorDatabase: MongoDB database instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if _database is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    return _database


def get_client() -> AsyncIOMotorClient:
    """
    Get current MongoDB client instance

    Returns:
        AsyncIOMotorClient: MongoDB client instance

    Raises:
        RuntimeError: If client is not initialized
    """
    if _client is None:
        raise RuntimeError("Database client is not initialized. Call init_db() first.")
    return _client
