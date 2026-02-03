from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
            
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.db


# Convenience function for dependency injection
async def get_database():
    """FastAPI dependency to get database instance."""
    return MongoDB.get_db()
