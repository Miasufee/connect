from typing import Tuple

import pyvips

from app.core.processing.image.image_presets import ImagePreset
from app.core.processing.image.utils import load_image, export_image


class ImageProcessor:
    """
    High-performance image processing using libvips (pyvips).
    """

    def __init__(self, data: bytes):
        self.image = load_image(data)

    # ------------------------
    # Metadata
    # ------------------------
    @property
    def size(self) -> Tuple[int, int]:
        return self.image.width, self.image.height

    @property
    def has_alpha(self) -> bool:
        return self.image.hasalpha()

    # ------------------------
    # Core operations
    # ------------------------
    def resize(
        self,
        width: int,
        height: int | None = None,
        crop: bool = False
    ) -> "ImageProcessor":

        if height:
            if crop:
                self.image = self.image.thumbnail_image(
                    width,
                    height=height,
                    crop=pyvips.Interesting.CENTRE
                )
            else:
                scale = min(
                    width / self.image.width,
                    height / self.image.height
                )
                self.image = self.image.resize(scale)
        else:
            self.image = self.image.thumbnail(width)

        return self

    def strip_metadata(self) -> "ImageProcessor":
        self.image = self.image.copy(interpretation="srgb")
        return self

    def ensure_rgb(self) -> "ImageProcessor":
        if self.image.bands == 4:
            self.image = self.image.flatten(background=[255, 255, 255])
        return self

    # ------------------------
    # Preset pipeline
    # ------------------------
    def apply_preset(self, preset: ImagePreset) -> bytes:
        self.resize(
            preset.width,
            preset.height,
            crop=preset.height is not None
        )

        self.ensure_rgb()
        self.strip_metadata()

        return export_image(
            self.image,
            preset.format,
            preset.quality
        )
