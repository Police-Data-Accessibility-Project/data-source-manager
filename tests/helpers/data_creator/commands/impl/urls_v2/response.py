from pydantic import BaseModel

from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.data_creator.models.creation_info.url import URLCreationInfo


class URLsV2Response(BaseModel):
    urls_by_status: dict[URLCreationEnum, URLCreationInfo] = {}
    urls_by_order: list[URLCreationInfo] = []