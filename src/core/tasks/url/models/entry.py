from pydantic import BaseModel

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.core import DSAppSyncAgenciesAddTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.core.tasks.url.operators.base import URLTaskOperatorBase


class URLTaskEntry(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    operator: URLTaskOperatorBase | DSSyncTaskOperatorBase
    enabled: bool