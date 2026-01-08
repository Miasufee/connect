from beanie import PydanticObjectId
from app.models import ReactionType
from app.models.interactions_models import PostReaction, PostComment
from app.crud.interactions_cruds.post_reaction_crud import post_reaction_crud
from app.crud.interactions_cruds.post_comment_crud import post_comment_crud


class CommentReactionService:

    @staticmethod
    async def toggle_like(*, comment_id: PydanticObjectId, user_id: PydanticObjectId):
        existing = await PostReaction.find_one(
            PostReaction.post_id == comment_id,
            PostReaction.user_id == user_id,
        )

        if not existing:
            await post_reaction_crud.create(
                post_id=comment_id,
                user_id=user_id,
                reaction=ReactionType.LIKE,
            )
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": 1}})
            return "liked"

        if existing.reaction == ReactionType.LIKE:
            await existing.delete()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": -1}})
            return "unliked"

        if existing.reaction == ReactionType.DISLIKE:
            existing.reaction = ReactionType.LIKE
            await existing.save()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": 1, "dislike_count": -1}})
            return "switched_to_like"
        return None

    @staticmethod
    async def toggle_dislike(*, comment_id: PydanticObjectId, user_id: PydanticObjectId):
        existing = await PostReaction.find_one(
            PostReaction.post_id == comment_id,
            PostReaction.user_id == user_id,
        )

        if not existing:
            await post_reaction_crud.create(
                post_id=comment_id,
                user_id=user_id,
                reaction=ReactionType.DISLIKE,
            )
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"dislike_count": 1}})
            return "disliked"

        if existing.reaction == ReactionType.DISLIKE:
            await existing.delete()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"dislike_count": -1}})
            return "undisliked"

        if existing.reaction == ReactionType.LIKE:
            existing.reaction = ReactionType.DISLIKE
            await existing.save()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": -1, "dislike_count": 1}})
            return "switched_to_dislike"
        return None
