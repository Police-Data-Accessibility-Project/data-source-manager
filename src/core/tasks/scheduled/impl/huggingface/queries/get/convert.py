from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse
from src.core.tasks.scheduled.impl.huggingface.queries.get.mappings import FINE_COARSE_RECORD_TYPE_MAPPING
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType


def convert_fine_to_coarse_record_type(
    fine_record_type: RecordType
) -> RecordTypeCoarse:
    return FINE_COARSE_RECORD_TYPE_MAPPING[fine_record_type]


def convert_validated_type_to_relevant(
    validated_type: ValidatedURLType
) -> bool:
    match validated_type:
        case ValidatedURLType.NOT_RELEVANT:
            return False
        case ValidatedURLType.DATA_SOURCE:
            return True
        case _:
            raise ValueError(f"Disallowed validated type: {validated_type}")