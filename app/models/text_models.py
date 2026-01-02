from beanie import Document
from app.models import TimestampMixin, TitleMixin, DescriptionMixin, ZawiyaIdMixin, UserIdMixin, GroupIdMixin


class TextPost(Document, TimestampMixin, TitleMixin, DescriptionMixin, ZawiyaIdMixin, UserIdMixin, GroupIdMixin):
    file_path: str

    class Settings:
        name = "text_posts"
