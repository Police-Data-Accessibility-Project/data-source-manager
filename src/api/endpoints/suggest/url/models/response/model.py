from pydantic import BaseModel

from src.api.endpoints.suggest.url.models.response.enums import URLSuggestResultEnum


class URLSuggestResponse(BaseModel):
    result: URLSuggestResultEnum
    url_id: int | None
    msg: str