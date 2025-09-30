from enum import Enum


class URLBatchSubmissionStatus(Enum):
    ALL_ACCEPTED = "all_accepted"
    PARTIALLY_ACCEPTED = "partially_accepted"
    ALL_REJECTED = "all_rejected"

class URLSubmissionStatus(Enum):
    ACCEPTED_AS_IS = "accepted_as_is"
    ACCEPTED_WITH_CLEANING = "accepted_with_cleaning"
    BATCH_DUPLICATE = "batch_duplicate"
    DATABASE_DUPLICATE = "database_duplicate"
    INVALID = "invalid"