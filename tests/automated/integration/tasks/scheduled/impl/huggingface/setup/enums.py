from enum import Enum


class PushToHuggingFaceTestSetupStatusEnum(Enum):
    NOT_VALIDATED = "NOT_VALIDATED"
    NOT_RELEVANT = "NOT_RELEVANT"
    DATA_SOURCE = "DATA_SOURCE"
