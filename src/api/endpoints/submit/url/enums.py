from enum import Enum

class URLSubmissionStatus(Enum):
    ACCEPTED_AS_IS = "accepted_as_is"
    ACCEPTED_WITH_CLEANING = "accepted_with_cleaning"
    DATABASE_DUPLICATE = "database_duplicate"
    INVALID = "invalid"