from pydantic import BaseModel, ConfigDict


class URLMapping(BaseModel):
    """Mapping between url and url_id."""
    model_config = ConfigDict(frozen=True)  # <- makes it immutable & hashable

    url: str
    url_id: int
