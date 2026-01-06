from beanie import PydanticObjectId
from app.crud import CrudBase
from app.models import ZawiyaPost, GroupPost

class PostReactionCrud:
    @staticmethod
    async def like_zawiya_post(post_id: PydanticObjectId):
        post = await ZawiyaPost.get(post_id)
        if post:
            post.like_count += 1
            await post.save()
            return post
        return None

    @staticmethod
    async def dislike_zawiya_post(post_id: PydanticObjectId):
        post = await ZawiyaPost.get(post_id)
        if post:
            post.dislike_count += 1
            await post.save()
            return post
        return None

    @staticmethod
    async def like_group_post(post_id: PydanticObjectId):
        post = await GroupPost.get(post_id)
        if post:
            post.like_count += 1
            await post.save()
            return post
        return None

    @staticmethod
    async def dislike_group_post(post_id: PydanticObjectId):
        post = await GroupPost.get(post_id)
        if post:
            post.dislike_count += 1
            await post.save()
            return post
        return None
