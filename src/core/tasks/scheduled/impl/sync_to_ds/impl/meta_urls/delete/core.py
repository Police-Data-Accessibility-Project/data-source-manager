from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase


class DSAppSyncMetaURLsDeleteTaskOperator(
    DSSyncTaskOperatorBase
):

    async def meets_task_prerequisites(self) -> bool:
        raise NotImplementedError

    async def inner_task_logic(self) -> None:
        raise NotImplementedError