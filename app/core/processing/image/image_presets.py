from dataclasses import dataclass

@dataclass(frozen=True)
class ImagePreset:
    width: int
    height: int | None
    quality: int
    format: str = "jpeg"


THUMBNAIL = ImagePreset(300, 300, 75)
POST_IMAGE = ImagePreset(1280, None, 82)
GALLERY_IMAGE = ImagePreset(2048, None, 85)
AVATAR = ImagePreset(256, 256, 80)
