from pydantic import BaseModel

from src.external.pdap.enums import DataSourcesURLStatus


class MetaURLSyncContentModel(BaseModel):
    url: str
    url_status: DataSourcesURLStatus = DataSourcesURLStatus.OK
    internet_archives_url: str | None = None
    agency_ids: list[int] = []
