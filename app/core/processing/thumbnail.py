import cv2
import numpy as np
from pathlib import Path
from typing import Union, Optional


class ThumbnailProcessor:
    """
    CPU-bound thumbnail processing using OpenCV.
    This file stays SYNC by design (fast + predictable).
    """

    @staticmethod
    def load(image: Union[bytes, str, Path]) -> np.ndarray:
        if isinstance(image, (str, Path)):
            data = np.fromfile(str(image), dtype=np.uint8)
        else:
            data = np.frombuffer(image, dtype=np.uint8)

        img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("Invalid image input")

        return img

    @staticmethod
    def resize(
        img: np.ndarray,
        width: Optional[int] = None,
        height: Optional[int] = None,
        keep_ratio: bool = True,
    ) -> np.ndarray:
        h, w = img.shape[:2]

        if width is None and height is None:
            raise ValueError("width or height required")

        if keep_ratio:
            if width and not height:
                height = int(h * width / w)
            elif height and not width:
                width = int(w * height / h)
            else:
                scale = min(width / w, height / h)
                width, height = int(w * scale), int(h * scale)

        return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    @staticmethod
    def encode(
        img: np.ndarray,
        format: str = "jpg",
        quality: int = 85,
    ) -> bytes:
        params = []
        if format in ("jpg", "jpeg"):
            params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif format == "webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, quality]
        elif format == "png":
            params = [cv2.IMWRITE_PNG_COMPRESSION, 3]

        ok, buf = cv2.imencode(f".{format}", img, params)
        if not ok:
            raise RuntimeError("Encoding failed")

        return buf.tobytes()

    @classmethod
    def create(
        cls,
        image: Union[bytes, str, Path],
        width: int,
        height: Optional[int] = None,
        format: str = "jpg",
        quality: int = 85,
    ) -> bytes:
        img = cls.load(image)
        img = cls.resize(img, width, height)
        return cls.encode(img, format, quality)
