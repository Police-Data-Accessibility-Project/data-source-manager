from pydantic import BaseModel

from src.util.models.full_url import FullURL


class DestinationURLSubsets(BaseModel):
    new_urls: list[FullURL]
    exist_with_alterations: list[FullURL]
    exist_as_is: list[FullURL]