"""MongoDB database connection and management."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup."""
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
        
        # Create indexes
        await create_indexes()
    except Exception as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        logger.warning("⚠️  Running without MongoDB - authentication will not work!")
        logger.warning("⚠️  Please set up MongoDB to use the application properly.")
        # Don't raise - allow app to start for testing
        # raise

async def close_mongo_connection():
    """Close MongoDB connection on shutdown."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Closed MongoDB connection")

async def create_indexes():
    """Create database indexes for better performance."""
    # Create unique index on email
    await mongodb.db.users.create_index("email", unique=True)
    
    # Create unique index on ocid
    await mongodb.db.users.create_index("ocid", unique=True)
    
    # Create index on reset_token for faster lookups
    await mongodb.db.users.create_index("reset_token", sparse=True)
    
    logger.info("Database indexes created")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return mongodb.db

