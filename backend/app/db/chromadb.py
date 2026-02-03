import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """ChromaDB connection manager."""
    
    client: Optional[chromadb.Client] = None
    
    @classmethod
    def connect(cls):
        """Connect to ChromaDB."""
        try:
            # For external ChromaDB server
            if settings.CHROMA_HOST != "localhost" or settings.ENVIRONMENT == "production":
                cls.client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT
                )
            else:
                # For local development with persistent storage
                cls.client = chromadb.Client(
                    ChromaSettings(
                        persist_directory=settings.CHROMA_PERSIST_DIR,
                        anonymized_telemetry=False
                    )
                )
            
            logger.info(f"Connected to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            
        except Exception as e:
            logger.error(f"Could not connect to ChromaDB: {e}")
            raise
    
    @classmethod
    def get_client(cls):
        """Get ChromaDB client instance."""
        if cls.client is None:
            cls.connect()
        return cls.client
    
    @classmethod
    def get_or_create_collection(cls, collection_name: str):
        """
        Get or create a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection instance
        """
        client = cls.get_client()
        return client.get_or_create_collection(name=collection_name)


# Convenience function for dependency injection
def get_chroma_client():
    """Get ChromaDB client instance."""
    return ChromaDBManager.get_client()
