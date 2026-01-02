from typing import List, Optional, Dict, Any
from bson import ObjectId
from beanie import SortDirection

from app.crud.crud_base import CrudBase
from app.models import Content, VisibilityStatus, ContentType


class ContentCrud(CrudBase[Content]):
    def __init__(self):
        super().__init__(Content)

    # ---------------- CREATE ----------------

    async def create_content(
        self,
        *,
        zawiya_id: ObjectId,
        author_id: ObjectId,
        content_type: ContentType,
        title: Optional[str] = None,
        text: Optional[str] = None,
        group_id: Optional[ObjectId] = None,
        visibility: VisibilityStatus = VisibilityStatus.PUBLIC,
    ) -> Content:
        content = Content(
            zawiya_id=zawiya_id,
            author_id=author_id,
            content_type=content_type,
            title=title,
            text=text,
            group_id=group_id,
            visibility=visibility,
        )
        return await content.insert()

    # ---------------- GET ONE ----------------

    async def get_by_id(
        self,
        content_id: ObjectId,
    ) -> Optional[Content]:
        return await self.model.find_one(
            {
                "_id": content_id,
                "is_deleted": False,
            }
        )

    # ---------------- LIST / FILTER ----------------

    async def list(
        self,
        filters: Dict[str, Any],
        *,
        skip: int = 0,
        limit: int = 20,
        order_desc: bool = True,
    ) -> List[Content]:
        direction = (
            SortDirection.DESCENDING
            if order_desc
            else SortDirection.ASCENDING
        )

        return await self.model.find(filters)\
            .sort("created_at", direction)\
            .skip(skip)\
            .limit(limit)\
            .to_list()

    # ---------------- UPDATE ----------------

    async def update_content(
        self,
        content_id: ObjectId,
        data: Dict[str, Any],
    ) -> Optional[Content]:
        content = await self.get_by_id(content_id)
        if not content:
            return None

        for key, value in data.items():
            setattr(content, key, value)

        await content.save()
        return content

    # ---------------- SOFT DELETE ----------------

    async def soft_delete(
        self,
        content_id: ObjectId,
    ) -> bool:
        content = await self.get_by_id(content_id)
        if not content:
            return False

        content.is_deleted = True
        await content.save()
        return True
