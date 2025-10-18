from pydantic import BaseModel

from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.models.full_url import FullURL


class URLProbeResponseOuterWrapper(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    original_url: FullURL
    response: URLProbeResponse | URLProbeRedirectResponsePair

    @property
    def is_redirect(self) -> bool:
        return isinstance(self.response, URLProbeRedirectResponsePair)
