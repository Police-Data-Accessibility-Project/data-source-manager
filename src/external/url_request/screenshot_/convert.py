from PIL import Image
from io import BytesIO

from PIL.ImageFile import ImageFile

from src.external.url_request.screenshot_.constants import COMPRESSION_QUALITY


def convert_png_to_webp(png: bytes) -> bytes:
    image: ImageFile = Image.open(BytesIO(png))
    output = BytesIO()
    image.save(output, format="WEBP", quality=COMPRESSION_QUALITY)
    return output.getvalue()
