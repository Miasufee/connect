from typing import List, Dict
from beanie import PydanticObjectId
from fastapi import BackgroundTasks
import aioredis
import asyncio
import json

from app.crud.content.audio_crud import audio_crud
from app.crud.content.image_crud import image_gallery_crud
from app.crud.content.post_crud import zawiya_post_crud, group_post_crud
from app.crud.content.video_crud import video_crud

from app.crud.interactions_cruds.like_dislike_crud import PostReactionCrud

# ---------------------- REDIS SETUP ----------------------
redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
FEED_TTL = 60       # seconds
MEDIA_TTL = 300     # seconds per post media

# ---------------------- FEED SERVICE ----------------------
class UnifiedFeedService:

    # ----------------- INTERNAL CACHING -----------------
    @staticmethod
    async def _cache(key: str, value: dict, ttl: int = FEED_TTL):
        await redis.set(key, json.dumps(value, default=str), ex=ttl)

    @staticmethod
    async def _get_cached(key: str):
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    @staticmethod
    async def _refresh_cache(key: str, fetch_func, *args, **kwargs):
        result = await fetch_func(*args, **kwargs)
        await UnifiedFeedService._cache(key, result)

    # ----------------- MEDIA CACHE -----------------
    @staticmethod
    async def _cache_media(post_id: str, media: dict):
        key = f"post_media:{post_id}"
        await redis.set(key, json.dumps(media, default=str), ex=MEDIA_TTL)

    @staticmethod
    async def _get_cached_media(post_id: str):
        key = f"post_media:{post_id}"
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    @staticmethod
    async def _attach_media(post: Dict) -> Dict:
        post_id = str(post.get("content_id"))
        media = await UnifiedFeedService._get_cached_media(post_id)
        if not media:
            media = {
                "videos": await video_crud.get_multi(filters={"content_id": post_id}),
                "audios": await audio_crud.get_multi(filters={"content_id": post_id}),
                "images": await image_gallery_crud.get_multi(filters={"content_id": post_id}),
            }
            await UnifiedFeedService._cache_media(post_id, media)
        post["media"] = media
        return post

    @staticmethod
    async def _attach_media_bulk(posts: List[Dict]) -> List[Dict]:
        return await asyncio.gather(*[UnifiedFeedService._attach_media(p) for p in posts])

    # ----------------- GENERIC FEED FETCHER -----------------
    @staticmethod
    async def _fetch_feed_with_cache(
        key: str,
        fetch_func,
        background_tasks: BackgroundTasks = None,
        *args, **kwargs
    ):
        cached = await UnifiedFeedService._get_cached(key)
        if cached:
            if background_tasks:
                background_tasks.add_task(UnifiedFeedService._refresh_cache, key, fetch_func, *args, **kwargs)
            return cached

        feed = await fetch_func(*args, **kwargs)
        if "items" in feed:
            feed["items"] = await UnifiedFeedService._attach_media_bulk(feed["items"])
        await UnifiedFeedService._cache(key, feed)
        return feed

    # ----------------- FEEDS -----------------
    @staticmethod
    async def for_you(user_id: PydanticObjectId, page: int = 1, per_page: int = 20, background_tasks: BackgroundTasks = None):
        key = f"for_you:{user_id}:{page}"
        return await UnifiedFeedService._fetch_feed_with_cache(key, zawiya_post_crud.feed_for_you, background_tasks, page, per_page)

    @staticmethod
    async def following(user_id: PydanticObjectId, following_zawiyas: List[PydanticObjectId], page: int = 1, per_page: int = 20, background_tasks: BackgroundTasks = None):
        key = f"following:{user_id}:{page}"
        return await UnifiedFeedService._fetch_feed_with_cache(key, zawiya_post_crud.feed_following, background_tasks, following_zawiyas, page, per_page)

    @staticmethod
    async def live(user_id: PydanticObjectId, page: int = 1, per_page: int = 20, background_tasks: BackgroundTasks = None):
        key = f"live:{user_id}:{page}"
        return await UnifiedFeedService._fetch_feed_with_cache(key, zawiya_post_crud.feed_live, background_tasks, page, per_page)

    @staticmethod
    async def by_zawiya(zawiya_id: PydanticObjectId, page: int = 1, per_page: int = 20, background_tasks: BackgroundTasks = None):
        key = f"zawiya_feed:{zawiya_id}:{page}"
        return await UnifiedFeedService._fetch_feed_with_cache(key, zawiya_post_crud.feed_by_zawiya, background_tasks, zawiya_id, page, per_page)

    @staticmethod
    async def by_group(group_id: PydanticObjectId, page: int = 1, per_page: int = 20, background_tasks: BackgroundTasks = None):
        key = f"group_feed:{group_id}:{page}"
        return await UnifiedFeedService._fetch_feed_with_cache(key, group_post_crud.feed_by_group, background_tasks, group_id, page, per_page)

    # ----------------- POST INTERACTIONS -----------------
    @staticmethod
    async def like_post(post_id):
        return await PostReactionCrud.like_zawiya_post(post_id)

    @staticmethod
    async def dislike_post(post_id):
        return await PostReactionCrud.dislike_zawiya_post(post_id)
