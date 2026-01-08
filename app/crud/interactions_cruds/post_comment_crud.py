from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.interactions_models import PostComment


class PostCommentCrud(CrudBase[PostComment]):
    """ PostComment Crud Management """
    def __init__(self):
        super().__init__(PostComment)

    async def hot_comments(self, post_id: PydanticObjectId, limit: int = 20):
        pipeline = [
            {
                "$match": {
                    "post_id": post_id,
                    "parent_comment_id": None,
                    "is_deleted": False,
                    "is_shadow_banned": False,
                }
            },
            {
                "$addFields": {
                    "age_hours": {
                        "$divide": [
                            {"$subtract": [datetime.now(timezone.utc), "$created_at"]},
                            1000 * 60 * 60,
                        ]
                    },
                    "score": {
                        "$divide": [
                            {"$subtract": ["$like_count", "$dislike_count"]},
                            {"$pow": [{"$add": ["$age_hours", 2]}, 1.5]},
                        ]
                    },
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": limit},
        ]
        return self.aggregate(pipeline)

post_comment_crud = PostCommentCrud()