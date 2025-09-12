from enum import Enum


class URLCreationEnum(Enum):
    OK = "ok"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    ERROR = "error"
    NOT_RELEVANT = "not_relevant"
    DUPLICATE = "duplicate"
    NOT_FOUND = "not_found"