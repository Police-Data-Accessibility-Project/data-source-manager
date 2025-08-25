from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.enums import \
    PushToHuggingFaceTestSetupStatusEnum

def convert_test_status_to_validated_status(
    status: PushToHuggingFaceTestSetupStatusEnum
) -> ValidatedURLType:
    match status:
        case PushToHuggingFaceTestSetupStatusEnum.DATA_SOURCE:
            return ValidatedURLType.DATA_SOURCE
        case PushToHuggingFaceTestSetupStatusEnum.NOT_RELEVANT:
            return ValidatedURLType.NOT_RELEVANT
        case _:
            raise ValueError(f"Invalid test status for function: {status}")