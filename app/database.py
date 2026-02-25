"""
MongoDB Database Connection
"""

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas only (no local fallback)
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "crop_disease_db")

# Global database instance
db = None
client = None


async def connect_db():
    """Connect to MongoDB Atlas on startup."""
    global db, client
    if not MONGODB_URL:
        print("[ERROR] MONGODB_URL is not set. Set it in backend/.env to your MongoDB Atlas connection string.")
        return
    try:
        client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        db = client[DATABASE_NAME]
        await client.admin.command("ping")
        print("[SUCCESS] Connected to MongoDB Atlas, DB:", DATABASE_NAME)

        # Create indexes for fast analytics + history queries
        try:
            await db.predictions.create_index(
                [("user_id", 1), ("created_at", -1)], background=True
            )
            await db.predictions.create_index(
                [("user_id", 1), ("prediction.disease_name", 1)], background=True
            )
            print("[SUCCESS] MongoDB indexes ensured")
        except Exception as idx_err:
            print(f"[WARNING] Index creation warning (non-fatal): {idx_err}")
    except Exception as e:
        db = None
        client = None
        print(f"[ERROR] MongoDB Atlas connection error: {e}")


async def close_db():
    """Close MongoDB connection on shutdown."""
    global client
    if client:
        client.close()
        print("[SUCCESS] MongoDB connection closed")


def get_db():
    """
    Get database instance.

    Raises a clear runtime error if the database is not initialized so that
    FastAPI returns a meaningful 500 instead of an obscure AttributeError.
    """
    if db is None:
        raise RuntimeError(
            "Database is not initialized. "
            "Set MONGODB_URL in backend/.env to your MongoDB Atlas connection string."
        )
    return db
