from pydantic import BaseModel


class MuckrockAgencyIDSubtaskParams(BaseModel):
    url_id: int
    collector_metadata: dict