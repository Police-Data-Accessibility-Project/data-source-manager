from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum


def convert_url_creation_enum_to_url_status(url_creation_enum: URLCreationEnum) -> URLStatus:
    match url_creation_enum:
        case URLCreationEnum.OK:
            return URLStatus.OK
        case URLCreationEnum.SUBMITTED:
            return URLStatus.OK
        case URLCreationEnum.VALIDATED:
            return URLStatus.OK
        case URLCreationEnum.NOT_RELEVANT:
            return URLStatus.OK
        case URLCreationEnum.ERROR:
            return URLStatus.ERROR
        case URLCreationEnum.DUPLICATE:
            return URLStatus.DUPLICATE
        case URLCreationEnum.NOT_FOUND:
            return URLStatus.NOT_FOUND
        case _:
            raise ValueError(f"Unknown URLCreationEnum: {url_creation_enum}")

def convert_url_creation_enum_to_validated_type(
    url_creation_enum: URLCreationEnum
) -> URLValidatedType:
    match url_creation_enum:
        case URLCreationEnum.SUBMITTED:
            return URLValidatedType.DATA_SOURCE
        case URLCreationEnum.VALIDATED:
            return URLValidatedType.DATA_SOURCE
        case URLCreationEnum.NOT_RELEVANT:
            return URLValidatedType.NOT_RELEVANT
        case _:
            raise ValueError(f"Unknown URLCreationEnum: {url_creation_enum}")