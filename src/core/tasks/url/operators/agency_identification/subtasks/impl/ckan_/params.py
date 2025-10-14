from pydantic import BaseModel


class CKANAgencyIDSubtaskParams(BaseModel):
    url_id: int
    collector_metadata: dict