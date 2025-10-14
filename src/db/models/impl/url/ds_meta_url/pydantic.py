from pydantic import BaseModel

from src.db.models.impl.url.ds_meta_url.sqlalchemy import URLDSMetaURL


class URLDSMetaURLPydantic(BaseModel):

    url_id: int
    ds_meta_url_id: int
    agency_id: int

    @classmethod
    def sa_model(cls) -> type[URLDSMetaURL]:
        return URLDSMetaURL