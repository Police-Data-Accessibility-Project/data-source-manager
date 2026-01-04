from pydantic import BaseModel

from src.db.dtos.url.mapping_.full import FullURLMapping
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


class URLProbeTDO(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    url_mapping: FullURLMapping
    response: URLProbeResponseOuterWrapper | None = None
