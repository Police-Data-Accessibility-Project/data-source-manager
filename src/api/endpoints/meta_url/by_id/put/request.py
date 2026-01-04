from pydantic import BaseModel


class UpdateMetaURLRequest(BaseModel):
    url: str | None = None
    name: str | None = None
    description: str | None = None

    batch_id: int | None = None

