from typing import Optional

from pydantic import BaseModel

from src.api.shared.models.request_base import RequestBase


class URLAgencyAnnotationPostInfo(RequestBase):
    is_new: bool = False
    suggested_agency: int | None = None
