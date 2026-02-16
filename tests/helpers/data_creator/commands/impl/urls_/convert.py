from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum

def convert_url_creation_enum_to_validated_type(
    url_creation_enum: URLCreationEnum
) -> URLType:
    match url_creation_enum:
        case URLCreationEnum.SUBMITTED:
            return URLType.DATA_SOURCE
        case URLCreationEnum.VALIDATED:
            return URLType.DATA_SOURCE
        case URLCreationEnum.NOT_RELEVANT:
            return URLType.NOT_RELEVANT
        case _:
            raise ValueError(f"Unknown URLCreationEnum: {url_creation_enum}")