import asyncio
from functools import partial
from typing import Iterable, List, Union
from pathlib import Path

from .thumbnail import ThumbnailProcessor


class AsyncThumbnailService:
    """
    Async wrapper around OpenCV thumbnail processor.
    Uses thread pool for CPU-bound tasks.
    """

    @staticmethod
    async def generate(
        image: Union[bytes, str, Path],
        width: int,
        height: int | None = None,
        format: str = "jpg",
        quality: int = 85,
    ) -> bytes:
        loop = asyncio.get_running_loop()

        func = partial(
            ThumbnailProcessor.create,
            image=image,
            width=width,
            height=height,
            format=format,
            quality=quality,
        )

        return await loop.run_in_executor(None, func)

    @classmethod
    async def generate_batch(
        cls,
        images: Iterable[Union[bytes, str, Path]],
        width: int,
        height: int | None = None,
        format: str = "jpg",
        quality: int = 85,
        concurrency: int = 4,
    ) -> List[bytes]:
        sem = asyncio.Semaphore(concurrency)

        async def _run(img):
            async with sem:
                return await cls.generate(
                    img, width, height, format, quality
                )

        return await asyncio.gather(*(_run(img) for img in images))
