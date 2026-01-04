from pydantic import BaseModel

from src.db.dtos.url.mapping_.full import FullURLMapping
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.external.url_request.probe.models.response import URLProbeResponse


class URLResponseMapping(BaseModel):
    url_mapping: FullURLMapping
    response: URLProbeResponse