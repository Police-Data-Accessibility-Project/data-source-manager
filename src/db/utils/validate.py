from typing import Protocol
from urllib.parse import urlparse

from pydantic import BaseModel


def validate_has_protocol(obj: object, protocol: type[Protocol]):
    if not isinstance(obj, protocol):
        raise TypeError(f"Class must implement {protocol} protocol.")

def validate_all_models_of_same_type(objects: list[object]):
    first_model = objects[0]
    if not all(isinstance(model, type(first_model)) for model in objects):
        raise TypeError("Models must be of the same type")

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        # If scheme is missing, `netloc` will be empty, so we check path too
        if result.scheme in ("http", "https") and result.netloc:
            return True
        if not result.scheme and result.path:
            # no scheme, treat path as potential domain
            return "." in result.path
        return False
    except ValueError:
        return False
