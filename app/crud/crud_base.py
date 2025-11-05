from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from beanie import Document, SortDirection
from pymongo.results import InsertManyResult

ModelType = TypeVar("ModelType", bound=Document)


class CrudBase(Generic[ModelType]):
    """Reusable CRUD base for Beanie models with pagination, sorting, and filters."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ---------- HELPERS ----------

    @staticmethod
    def _filters(filters: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Merge and clean up filters."""
        merged = {**(filters or {}), **kwargs}
        return {k: v for k, v in merged.items() if v is not None}

    @staticmethod
    def _sort(
        order_by: Optional[Union[str, tuple[str, SortDirection], list[tuple[str, SortDirection]]]] = None
    ) -> Optional[list[tuple[str, SortDirection]]]:
        """
        Converts string or list input to Beanie-compatible sort tuples.
        """
        if not order_by:
            return None

        if isinstance(order_by, str):
            return [(order_by, SortDirection.ASCENDING)]
        elif isinstance(order_by, tuple):
            field, direction = order_by
            return [(field, direction)]
        elif isinstance(order_by, list):
            # Ensure each item is a tuple with SortDirection
            return [(field, direction if isinstance(direction, SortDirection) else SortDirection.ASCENDING)
                    for field, direction in order_by]
        return None

    # ---------- CREATE ----------

    async def create(self, **kwargs: Any) -> ModelType:
        """Insert a single document."""
        doc = self.model(**kwargs)
        return await doc.insert()

    async def bulk_create(self, objects: List[Dict[str, Any]]) -> InsertManyResult:
        """Insert multiple documents."""
        docs = [self.model(**obj) for obj in objects]
        return await self.model.insert_many(docs)

    # ---------- READ ----------

    async def get(self, obj_id: Any) -> Optional[ModelType]:
        """Get document by ID."""
        return await self.model.get(obj_id)

    async def get_one(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[ModelType]:
        """Find one document by filters."""
        return await self.model.find_one(self._filters(filters, **kwargs))

    async def get_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Union[str, tuple[str, SortDirection], list[tuple[str, SortDirection]]]] = None,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> List[ModelType]:
        query = self.model.find(self._filters(filters, **kwargs))

        if sort := self._sort(order_by):
            query = query.sort(*sort)

        return await query.skip(skip).limit(limit).to_list()

    async def count(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> int:
        return await self.model.find(self._filters(filters, **kwargs)).count()

    # ---------- UPDATE ----------

    async def update(self, obj_id: Any, update_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update document by ID."""
        obj = await self.model.get(obj_id)
        if not obj:
            return None
        for k, v in update_data.items():
            setattr(obj, k, v)
        await obj.save()
        return obj

    async def update_by_filter(
        self,
        filters: Optional[Dict[str, Any]] = None,
        update_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[ModelType]:
        """Find one document and update it."""
        update_data = update_data or {}
        obj = await self.model.find_one(self._filters(filters, **kwargs))
        if not obj:
            return None
        for k, v in update_data.items():
            setattr(obj, k, v)
        await obj.save()
        return obj

    # ---------- DELETE ----------

    async def delete(self, obj_id: Any) -> bool:
        """Delete document by ID."""
        obj = await self.model.get(obj_id)
        if obj:
            await obj.delete()
            return True
        return False

    async def delete_by_filter(self, filters: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        """Delete a single document by filter."""
        obj = await self.model.find_one(self._filters(filters, **kwargs))
        if obj:
            await obj.delete()
            return True
        return False

    # ---------- UPSERT ----------

    async def upsert(
        self,
        filters: Optional[Dict[str, Any]] = None,
        update_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ModelType:
        """Update or insert if not exists."""
        update_data = update_data or {}
        merged = self._filters(filters, **kwargs)
        existing = await self.model.find_one(merged)
        if existing:
            for k, v in update_data.items():
                setattr(existing, k, v)
            await existing.save()
            return existing
        new_doc = self.model(**{**merged, **update_data})
        return await new_doc.insert()

    # ---------- PAGINATION ----------

    async def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Return paginated data with metadata."""
        page = max(page, 1)
        total = await self.count(filters, **kwargs)
        skip = (page - 1) * per_page
        items = await self.get_multi(filters, order_by, skip, per_page, **kwargs)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    # ---------- AGGREGATION ----------

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run custom MongoDB aggregation pipeline."""
        return await self.model.aggregate(pipeline).to_list()

    # ---------- BATCH ----------

    async def get_by_ids(self, ids: List[Any]) -> List[ModelType]:
        """Get documents by a list of IDs."""
        return await self.model.find({"_id": {"$in": ids}}).to_list()
