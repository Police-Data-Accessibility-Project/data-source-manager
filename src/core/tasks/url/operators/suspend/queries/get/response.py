from pydantic import BaseModel


class GetURLsForSuspensionResponse(BaseModel):
    url_id: int