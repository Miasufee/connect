
from beanie import Document, PydanticObjectId
from app.models import TimestampMixin, SoftDeleteMixin

class ImageAudioContent(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
):
    image_gallery_id: PydanticObjectId
    audio_id: PydanticObjectId | None = None

    class Settings:
        name = "image_audio_contents"
