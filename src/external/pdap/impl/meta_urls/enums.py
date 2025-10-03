from enum import Enum


class SubmitMetaURLsStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ALREADY_EXISTS = "already_exists"