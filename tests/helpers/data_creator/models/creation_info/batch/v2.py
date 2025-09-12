from pydantic import BaseModel

from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.data_creator.models.creation_info.url import URLCreationInfo


class BatchURLCreationInfoV2(BaseModel):
    batch_id: int
    urls_by_status: dict[URLCreationEnum, URLCreationInfo] = {}

    @property
    def url_ids(self) -> list[int]:
        url_creation_infos = self.urls_by_status.values()
        url_ids = []
        for url_creation_info in url_creation_infos:
            url_ids.extend(url_creation_info.url_ids)
        return url_ids
