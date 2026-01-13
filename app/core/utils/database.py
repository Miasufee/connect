from __future__ import annotations

import sys
import logging
import pkgutil
import importlib
from typing import Type, List, Set

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie, Document

from app.core.utils.settings import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    # ----------------- PUBLIC -----------------

    async def connect(self, debug_models: bool = False):
        """Connect to MongoDB and initialize Beanie with all models."""
        if self.client:
            return  # Already connected

        try:
            mongo_url = settings.mongo_url
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[settings.MONGO_DB]

            # Test connection
            await self.client.admin.command("ping")

            # Discover models
            models = self._get_beanie_models()
            await init_beanie(
                database=self.db,
                document_models=models,
            )

            # Debug output
            if debug_models:
                self.print_models(models)
                self._warn_missing_models(models)

            logger.info("✅ MongoDB connected and Beanie initialized.")

        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            await self.disconnect()
            raise

    async def disconnect(self):
        """Disconnect MongoDB client."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB disconnected.")

    # ----------------- INTERNAL HELPERS -----------------

    @staticmethod
    def _import_all_model_modules():
        """
        Dynamically import all modules inside 'app.models' package so that
        Beanie can discover all Document subclasses.
        """
        import app.models as models_pkg

        for _, module_name, _ in pkgutil.iter_modules(models_pkg.__path__):
            importlib.import_module(f"{models_pkg.__name__}.{module_name}")

    @classmethod
    def _get_beanie_models(cls) -> List[Type[Document]]:
        """
        Collect all Beanie Document subclasses from imported modules.
        """
        cls._import_all_model_modules()

        models: List[Type[Document]] = []

        for module in sys.modules.values():
            try:
                for obj in vars(module).values():
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, Document)
                        and obj is not Document
                    ):
                        models.append(obj)
            except Exception:
                continue

        # Remove duplicates
        return list(set(models))

    # ----------------- DEBUG -----------------

    @staticmethod
    def print_models(models: List[Type[Document]]):
        """Print all discovered Beanie models."""
        logger.info("🟢 Discovered Beanie Models:")
        for model in sorted(models, key=lambda m: m.__name__):
            logger.info(f" - {model.__module__}.{model.__name__}")

    @staticmethod
    def _warn_missing_models(models: List[Type[Document]]):
        """
        Check all modules in app.models and warn if any Document subclass
        exists but wasn’t imported/discovered.
        """
        import app.models as models_pkg

        discovered: Set[str] = {f"{m.__module__}.{m.__name__}" for m in models}
        missing: List[str] = []

        for _, module_name, _ in pkgutil.iter_modules(models_pkg.__path__):
            full_module_name = f"{models_pkg.__name__}.{module_name}"
            try:
                mod = importlib.import_module(full_module_name)
                for obj in vars(mod).values():
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, Document)
                        and obj is not Document
                    ):
                        fq_name = f"{obj.__module__}.{obj.__name__}"
                        if fq_name not in discovered:
                            missing.append(fq_name)
            except Exception:
                continue

        if missing:
            logger.warning("⚠️  Beanie Document subclasses exist but were not imported:")
            for m in missing:
                logger.warning(f" - {m}")


# Global instance
mongodb = Database()
