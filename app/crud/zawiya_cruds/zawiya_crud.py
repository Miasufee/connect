from __future__ import annotations

import re
from typing import Optional
from beanie import PydanticObjectId

from app.crud.crud_base import CrudBase
from app.models.zawiya_models import Zawiya
from app.core.response.exceptions import Exceptions


class ZawiyaCrud(CrudBase[Zawiya]):

    def __init__(self):
        super().__init__(Zawiya)

    # ---------------- CREATE ----------------
    async def create_zawiya(self, *, title, name, description, owner_id):
        if await self.get_one(title=title):
            raise Exceptions.forbidden("Title already exists")

        if await self.get_one(name=name):
            raise Exceptions.forbidden("Name already exists")

        return await self.create(
            title=title,
            name=name,
            description=description,
            owner_id=owner_id,
            is_verified=False,
        )

    # ---------------- BASIC GET ----------------
    async def get_by_id(self, zawiya_id: PydanticObjectId):
        return await self.get(zawiya_id)

    async def get_by_title(self, title: str):
        return await self.get_one(title=title.strip())

    async def get_by_name(self, name: str):
        return await self.get_one(name=name.strip())

    # ---------------- SEARCH FILTER BUILDERS ----------------
    @staticmethod
    def _simple_filter(query: str) -> dict:
        regex = re.compile(re.escape(query), re.IGNORECASE)
        return {
            "$or": [
                {"title": regex},
                {"name": regex},
                {"description": regex},
            ]
        }

    @staticmethod
    def _multi_word_filter(query: str) -> dict:
        words = [re.escape(w) for w in query.split() if w]
        pattern = "".join(f"(?=.*{w})" for w in words)
        return {
            "$or": [
                {"title": {"$regex": pattern, "$options": "i"}},
                {"name": {"$regex": pattern, "$options": "i"}},
                {"description": {"$regex": pattern, "$options": "i"}},
            ]
        }

    # ---------------- SEARCH ----------------
    async def search(
        self,
        *,
        query: str,
        page: int,
        per_page: int,
        is_verified: Optional[bool] = None,
        multi_word: bool = False,
    ):
        filters = {"is_deleted": False}

        filters.update(
            self._multi_word_filter(query)
            if multi_word
            else self._simple_filter(query)
        )

        if is_verified is not None:
            filters["is_verified"] = is_verified

        return await self.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=("created_at", -1),
        )


zawiya_crud = ZawiyaCrud()
