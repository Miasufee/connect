from __future__ import annotations

from typing import Optional
from beanie import PydanticObjectId
from bson import ObjectId

from app.core.response.exceptions import Exceptions
from app.models.zawiya_models import (
    Zawiya,
    ZawiyaProfile,
    ZawiyaAnalytics,
    ZawiyaAdmin,
    ZawiyaRoles,
)
from app.crud.zawiya_cruds.zawiya_crud import zawiya_crud
from app.services.zawiya.zawiya_permissions import zawiya_permission


class ZawiyaService:

    # ---------------- CREATE ----------------
    async def create(self, *, title, name, description, owner_id):
        zawiya = await zawiya_crud.create_zawiya(
            title=title,
            name=name,
            description=description,
            owner_id=owner_id,
        )

        await ZawiyaProfile(zawiya_id=zawiya.id).insert()
        await ZawiyaAnalytics(zawiya_id=zawiya.id).insert()
        await ZawiyaAdmin(
            user_id=owner_id,
            zawiya_id=zawiya.id,
            role=ZawiyaRoles.SuperAdmin,
        ).insert()

        return zawiya

    # ---------------- GET (SMART) ----------------
    async def get(
        self,
        *,
        zawiya_id: str | PydanticObjectId | None = None,
        title: str | None = None,
        name: str | None = None,
        q: str | None = None,
    ) -> Zawiya:

        if zawiya_id:
            if isinstance(zawiya_id, str) and ObjectId.is_valid(zawiya_id):
                zawiya = await zawiya_crud.get_by_id(PydanticObjectId(zawiya_id))
            elif isinstance(zawiya_id, PydanticObjectId):
                zawiya = await zawiya_crud.get_by_id(zawiya_id)
            else:
                zawiya = None

            if zawiya:
                return zawiya

        if title:
            zawiya = await zawiya_crud.get_by_title(title)
            if zawiya:
                return zawiya

        if name:
            zawiya = await zawiya_crud.get_by_name(name)
            if zawiya:
                return zawiya

        if q:
            result = await self.search(query=q, page=1, per_page=1)
            if result["items"]:
                return result["items"][0]

        raise Exceptions.not_found("Zawiya not found")

    # ---------------- SEARCH ----------------
    async def search(
        self,
        *,
        query: str,
        page: int = 1,
        per_page: int = 20,
        is_verified: Optional[bool] = None,
    ):
        query = query.strip().replace('"', "")
        if not query:
            raise Exceptions.bad_request("Search query cannot be empty")

        multi_word = len(query.split()) > 1

        result = await zawiya_crud.search(
            query=query,
            page=page,
            per_page=per_page,
            is_verified=is_verified,
            multi_word=multi_word,
        )

        if not result["items"]:
            raise Exceptions.not_found("No zawiya matched your search")

        return result

        # ---------------- LIST (PAGINATION) ----------------
    @staticmethod
    async def list(*, page=1, per_page=20, is_verified=None):
        filters = {}
        if is_verified is not None:
            filters["is_verified"] = is_verified

        return await zawiya_crud.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
        )
    # ---------------- VERIFY ----------------
    async def verify(self, *, zawiya_id, verified_by):
        return await zawiya_crud.update(
            zawiya_id,
            {"is_verified": True, "verified_by": verified_by},
        )

    # ---------------- UPDATE ----------------
    async def update(self, *, zawiya_id, data, user_id):
        zawiya = await zawiya_crud.get(zawiya_id)
        if not zawiya:
            raise Exceptions.not_found("Zawiya not found")

        await zawiya_permission.require_owner(zawiya, user_id)
        return await zawiya_crud.update(zawiya_id, data)

    # ---------------- SOFT DELETE ----------------
    async def soft_delete(self, *, zawiya_id, user_id):
        zawiya = await zawiya_crud.get(zawiya_id)
        if not zawiya:
            raise Exceptions.not_found("Zawiya not found")

        await zawiya_permission.require_owner(zawiya, user_id)
        await zawiya.soft_delete()
        return {"deleted": True}


zawiya_service = ZawiyaService()