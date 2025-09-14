from PIL import Image
from io import BytesIO

from PIL.ImageFile import ImageFile


def convert_png_to_webp(png: bytes) -> bytes:
    image: ImageFile = Image.open(BytesIO(png))
    output = BytesIO()
    image.save(output, format="WEBP", lossless=True)
    return output.getvalue()
