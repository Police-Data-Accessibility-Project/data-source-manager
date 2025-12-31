from enum import Enum


class BatchURLStatusViewEnum(Enum):
    ERROR = "Error"
    NO_URLS = "No URLs"
    LABELING_COMPLETE = "Labeling Complete"
    HAS_UNLABELED_URLS = "Has Unlabeled URLs"