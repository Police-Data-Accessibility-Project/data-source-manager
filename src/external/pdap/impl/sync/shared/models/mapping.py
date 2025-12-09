from pydantic import BaseModel


class DSSyncIDMapping(BaseModel):
    ds_app_link_id: int
    entity_id: int