from pydantic import BaseModel

from src.core.tasks.scheduled.impl.internet_archives.save.models.mapping import URLInternetArchivesSaveResponseMapping


class IASaveURLMappingSubsets(BaseModel):
    error: list[URLInternetArchivesSaveResponseMapping] = []
    success: list[URLInternetArchivesSaveResponseMapping] = []