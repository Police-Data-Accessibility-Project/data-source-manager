from pydantic import BaseModel, ConfigDict

from src.util.models.full_url import FullURL


class FullURLMapping(BaseModel):
    """Mapping between full URL and url_id"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True # <- makes it immutable & hashable
    )

    full_url: FullURL
    url_id: int