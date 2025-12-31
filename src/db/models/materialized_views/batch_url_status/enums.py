from enum import Enum


class BatchURLStatusEnum(Enum):
    ERROR = "Error"
    UNLABELED_URLS = "Has Unlabeled URLs"
    NO_URLS = "No URLs"
    LABELING_COMPLETE = "Labeling Complete"