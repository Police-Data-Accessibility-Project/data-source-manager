from enum import Enum


class TaskStatus(Enum):
    COMPLETE = "complete"
    IN_PROCESS = "in-process"
    ERROR = "error"
    ABORTED = "aborted"
    NEVER_COMPLETED = "never-completed"
