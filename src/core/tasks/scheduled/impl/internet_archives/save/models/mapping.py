from pydantic import BaseModel

from src.external.internet_archives.models.save_response import InternetArchivesSaveResponseInfo


class URLInternetArchivesSaveResponseMapping(BaseModel):
    url: str
    response: InternetArchivesSaveResponseInfo