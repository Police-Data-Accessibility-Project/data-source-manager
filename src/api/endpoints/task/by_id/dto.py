import datetime
from typing import Optional

from pydantic import BaseModel

from src.db.models.impl.task.enums import TaskStatus
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.enums import TaskType
from src.core.enums import BatchStatus


class TaskInfo(BaseModel):
    task_type: TaskType
    task_status: TaskStatus
    updated_at: datetime.datetime
    error_info: str | None = None
    urls: list[URLInfo]
    url_errors: list[URLErrorInfoPydantic]