import abc
import traceback
from abc import ABC

from src.core.tasks.url.operators.location_id.subtasks.models.run_info import LocationIDSubtaskRunInfo
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic
from src.db.models.impl.url.suggestion.location.auto.suggestion.pydantic import LocationIDSubtaskSuggestionPydantic
from src.db.models.impl.url.task_error.pydantic_.insert import URLTaskErrorPydantic
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall


class LocationIDSubtaskOperatorBase(ABC):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int
    ) -> None:
        self.adb_client: AsyncDatabaseClient = adb_client
        self.task_id: int = task_id
        self.linked_urls: list[int] = []

    async def run(self) -> LocationIDSubtaskRunInfo:
        try:
            await self.inner_logic()
        except Exception as e:
            # Get stack trace
            stack_trace: str = traceback.format_exc()
            return LocationIDSubtaskRunInfo(
                error=f"{type(e).__name__}: {str(e)}: {stack_trace}",
                linked_url_ids=self.linked_urls
            )
        return LocationIDSubtaskRunInfo(
            linked_url_ids=self.linked_urls
        )

    @abc.abstractmethod
    async def inner_logic(self) -> LocationIDSubtaskRunInfo:
        raise NotImplementedError

    async def _upload_subtask_data(
        self,
        subtask_data_list: list[AutoLocationIDSubtaskData]
    ) -> None:

        subtask_models: list[AutoLocationIDSubtaskPydantic] = [
            subtask_data.pydantic_model
            for subtask_data in subtask_data_list
        ]
        subtask_ids: list[int] = await self.adb_client.bulk_insert(
            models=subtask_models,
            return_ids=True
        )
        suggestions: list[LocationIDSubtaskSuggestionPydantic] = []
        for subtask_id, subtask_info in zip(subtask_ids, subtask_data_list):
            suggestions_raw: list[LocationSuggestion] = subtask_info.suggestions
            for suggestion in suggestions_raw:
                suggestion_pydantic = LocationIDSubtaskSuggestionPydantic(
                    subtask_id=subtask_id,
                    location_id=suggestion.location_id,
                    confidence=suggestion.confidence,
                )
                suggestions.append(suggestion_pydantic)

        await self.adb_client.bulk_insert(
            models=suggestions,
        )

        error_infos: list[URLTaskErrorSmall] = []
        for subtask_info in subtask_data_list:
            if not subtask_info.has_error:
                continue
            error_info = URLTaskErrorSmall(
                url_id=subtask_info.url_id,
                error=subtask_info.error,
            )
            error_infos.append(error_info)

        await self.add_task_errors(error_infos)

    async def add_task_errors(
        self,
        errors: list[URLTaskErrorSmall]
    ) -> None:
        inserts: list[URLTaskErrorPydantic] = [
            URLTaskErrorPydantic(
                task_id=self.task_id,
                url_id=error.url_id,
                task_type=TaskType.LOCATION_ID,
                error=error.error
            )
            for error in errors
        ]
        await self.adb_client.bulk_insert(inserts)