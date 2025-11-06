
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.core.settings import settings
from app.models.user_models import User, VerificationCode, RefreshedToken, UserProfile, PhoneNumber, \
    UserPreferences
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self):
        """Connect to MongoDB and initialize Beanie"""
        if not self.client:
            try:
                # Get the connection URL from settings
                mongo_url = settings.mongo_url
                self.client = AsyncIOMotorClient(mongo_url)
                self.db = self.client[settings.MONGO_DB]

                # Test connection first
                await self.client.admin.command('ping')

                # Initialize Beanie
                await init_beanie(
                    database=self.db,
                    document_models=[
                        User,
                        UserProfile,
                        PhoneNumber,
                        UserPreferences,
                        VerificationCode,
                        RefreshedToken],
                )

            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                # Clean up on failure
                if self.client:
                    self.client.close()
                    self.client = None
                    self.db = None
                raise

    async def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None


mongodb = Database()
