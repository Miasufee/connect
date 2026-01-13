import pyvips
from io import BytesIO

def load_image(data: bytes) -> pyvips.Image:
    return pyvips.Image.new_from_buffer(data, "")


def export_image(
    image: pyvips.Image,
    format: str,
    quality: int
) -> bytes:
    return image.write_to_buffer(
        f".{format}",
        Q=quality,
        strip=True,
        optimize_coding=True
    )
