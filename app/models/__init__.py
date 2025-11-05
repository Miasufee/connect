# how to pass the db sesseion automatic to the crud base no nedd to call on every routes from typing import AsyncGenerator, cast
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# from beanie import init_beanie
# from app.core.settings import settings
# from app.models.user_models import User
#
#
# class Database:
#     """MongoDB connection manager (shared global instance)"""
#
#     def __init__(self):
#         self.client: AsyncIOMotorClient | None = None
#         self.db: AsyncIOMotorDatabase | None = None
#
#     async def connect(self):
#         """Connect to MongoDB and initialize Beanie"""
#         if not self.client:
#             self.client = AsyncIOMotorClient(settings.MONGO_URL)
#             self.db = self.client[settings.MONGO_DB]
#
#             # Initialize Beanie once
#             await init_beanie(
#                 database=cast(AsyncIOMotorDatabase, self.db),
#                 document_models=[
#                     User,  # add all models here
#                 ],
#             )
#             print("✅ MongoDB connected & Beanie initialized.")
#
#     async def disconnect(self):
#         """Close the MongoDB connection"""
#         if self.client:
#             self.client.close()
#             self.client = None
#             self.db = None
#             print("❌ MongoDB disconnected.")
#
#
# # Create global instance
# mongodb = Database()
#
#
# # Dependency (optional, for transactions or manual db access)
# async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
#     if not mongodb.db:
#         await mongodb.connect()
#     yield mongodb.db
#
#
# async def get_db_session() -> AsyncGenerator:
#     """MongoDB transaction session (optional use in routes)"""
#     if not mongodb.client:
#         await mongodb.connect()
#     async with await mongodb.client.start_session() as session:
#         yield session
#  from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable, Coroutine, Union
# from beanie import Document
# from pymongo.errors import PyMongoError, DuplicateKeyError
# import functools
# import logging
#
# from pymongo.results import InsertManyResult
#
# ModelType = TypeVar("ModelType", bound=Document)
# logger = logging.getLogger(__name__)
#
#
# def handle_db_errors(operation_name: str):
#     """Decorator for consistent error handling across all database operations."""
#
#     def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
#             try:
#                 return await func(*args, **kwargs)
#             except DuplicateKeyError as e:
#                 logger.error(f"[{operation_name}] Duplicate key error: {e}")
#                 raise
#             except PyMongoError as e:
#                 logger.error(f"[{operation_name}] Database error: {e}")
#                 raise
#             except Exception as e:
#                 logger.exception(f"[{operation_name}] Unexpected error: {e}")
#                 raise
#
#         return wrapper
#
#     return decorator
#
#
# class CrudBase(Generic[ModelType]):
#     """
#     A clean, production-ready CRUD base class for Beanie models.
#     Includes safe execution, pagination, aggregation, and upsert helpers.
#     """
#
#     def __init__(self, model: Type[ModelType]):
#         self.model = model
#
#     # ================== HELPERS ==================
#
#     @staticmethod
#     def _filters(filters: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
#         """Merge and clean filters, removing None values."""
#         merged = {**(filters or {}), **kwargs}
#         return {k: v for k, v in merged.items() if v is not None}
#
#     @staticmethod
#     def _sort(order_by: Optional[Union[str, List[str]]]) -> Optional[List[tuple]]:
#         """Convert order_by input to Beanie sort format."""
#         if not order_by:
#             return None
#         if isinstance(order_by, str):
#             order_by = [order_by]
#         return [(f.lstrip("-"), -1 if f.startswith("-") else 1) for f in order_by]
#
#     # ================== CREATE ==================
#
#     @handle_db_errors("create")
#     async def create(self, **kwargs: Any) -> ModelType:
#         """Create a single document."""
#         doc = self.model(**kwargs)
#         return await doc.insert()
#
#     @handle_db_errors("bulk_create")
#     async def bulk_create(self, objects: List[Dict[str, Any]]) -> InsertManyResult:
#         """Create multiple documents in batch."""
#         docs = [self.model(**obj) for obj in objects]
#         return await self.model.insert_many(docs)
#
#     # ================== READ ==================
#
#     @handle_db_errors("get")
#     async def get(self, obj_id: Any) -> Optional[ModelType]:
#         """Get document by ID."""
#         return await self.model.get(obj_id)
#
#     @handle_db_errors("get_one")
#     async def get_one(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[ModelType]:
#         """Get a single document matching filters."""
#         return await self.model.find_one(self._filters(filters, **kwargs))
#
#     @handle_db_errors("get_multi")
#     async def get_multi(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             order_by: Optional[Union[str, List[str]]] = None,
#             skip: int = 0,
#             limit: int = 100,
#             **kwargs
#     ) -> List[ModelType]:
#         """Get multiple documents with pagination and sorting."""
#         query = self.model.find(self._filters(filters, **kwargs))
#         if sort := self._sort(order_by):
#             query = query.sort(sort)
#         return await query.skip(skip).limit(limit).to_list()
#
#     @handle_db_errors("count")
#     async def count(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> int:
#         """Count documents matching filters."""
#         return await self.model.find(self._filters(filters, **kwargs)).count()
#
#     @handle_db_errors("exists")
#     async def exists(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
#         """Check if any document matches filters."""
#         return await self.model.find_one(self._filters(filters, **kwargs)) is not None
#
#     # ================== UPDATE ==================
#
#     @handle_db_errors("update")
#     async def update(self, obj_id: Any, update_data: Dict[str, Any]) -> Optional[ModelType]:
#         """Update document by ID."""
#         obj = await self.model.get(obj_id)
#         if not obj:
#             return None
#         for key, value in update_data.items():
#             setattr(obj, key, value)
#         await obj.save()
#         return obj
#
#     @handle_db_errors("update_by_filter")
#     async def update_by_filter(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             update_data: Dict[str, Any] = None,
#             **kwargs
#     ) -> Optional[ModelType]:
#         """Update first document matching filters."""
#         if update_data is None:
#             update_data = {}
#         obj = await self.model.find_one(self._filters(filters, **kwargs))
#         if not obj:
#             return None
#         for k, v in update_data.items():
#             setattr(obj, k, v)
#         await obj.save()
#         return obj
#
#     @handle_db_errors("bulk_update")
#     async def bulk_update(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             update_data: Dict[str, Any] = None,
#             **kwargs
#     ) -> int:
#         """Update multiple documents matching filters."""
#         if update_data is None:
#             update_data = {}
#         result = await self.model.find(self._filters(filters, **kwargs)).update_many({"$set": update_data})
#         return result.modified_count
#
#     # ================== DELETE ==================
#
#     @handle_db_errors("delete")
#     async def delete(self, obj_id: Any) -> bool:
#         """Delete document by ID."""
#         obj = await self.model.get(obj_id)
#         if obj:
#             await obj.delete()
#             return True
#         return False
#
#     @handle_db_errors("delete_by_filter")
#     async def delete_by_filter(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             **kwargs
#     ) -> bool:
#         """Delete first document matching filters."""
#         obj = await self.model.find_one(self._filters(filters, **kwargs))
#         if obj:
#             await obj.delete()
#             return True
#         return False
#
#     @handle_db_errors("bulk_delete")
#     async def bulk_delete(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             **kwargs
#     ) -> int:
#         """Delete multiple documents matching filters."""
#         result = await self.model.find(self._filters(filters, **kwargs)).delete_many()
#         return result.deleted_count
#
#     # ================== UPSERT ==================
#
#     @handle_db_errors("upsert")
#     async def upsert(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             update_data: Dict[str, Any] = None,
#             **kwargs
#     ) -> ModelType:
#         """Update existing document or create new one."""
#         if update_data is None:
#             update_data = {}
#         merged_filters = self._filters(filters, **kwargs)
#         existing = await self.model.find_one(merged_filters)
#         if existing:
#             for k, v in update_data.items():
#                 setattr(existing, k, v)
#             await existing.save()
#             return existing
#         new_doc = self.model(**{**merged_filters, **update_data})
#         return await new_doc.insert()
#
#     # ================== PAGINATION ==================
#
#     @handle_db_errors("paginate")
#     async def paginate(
#             self,
#             page: int = 1,
#             per_page: int = 20,
#             filters: Optional[Dict[str, Any]] = None,
#             order_by: Optional[Union[str, List[str]]] = None,
#             **kwargs
#     ) -> Dict[str, Any]:
#         """Paginate results with metadata."""
#         page = max(page, 1)
#         total = await self.count(filters, **kwargs)
#         skip = (page - 1) * per_page
#         items = await self.get_multi(filters, order_by, skip, per_page, **kwargs)
#         total_pages = (total + per_page - 1) // per_page if total > 0 else 0
#
#         return {
#             "items": items,
#             "total": total,
#             "page": page,
#             "per_page": per_page,
#             "total_pages": total_pages,
#             "has_next": page < total_pages,
#             "has_prev": page > 1,
#         }
#
#     # ================== AGGREGATION ==================
#
#     @handle_db_errors("aggregate")
#     async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Execute aggregation pipeline."""
#         return await self.model.aggregate(pipeline).to_list()
#
#     # ================== BATCH OPERATIONS ==================
#
#     @handle_db_errors("get_by_ids")
#     async def get_by_ids(self, ids: List[Any]) -> List[ModelType]:
#         """Get multiple documents by their IDs."""
#         return await self.model.find({"_id": {"$in": ids}}).to_list()
#
#     @handle_db_errors("update_or_create")
#     async def update_or_create(
#             self,
#             filters: Optional[Dict[str, Any]] = None,
#             defaults: Dict[str, Any] = None,
#             **kwargs
#     ) -> ModelType:
#         """Alias for upsert with more semantic naming."""
#         if defaults is None:
#             defaults = {}
#         return await self.upsert(filters, defaults, **kwargs)