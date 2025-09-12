import abc
import traceback
from abc import ABC

from src.core.tasks.url.operators.agency_identification.subtasks.models.run_info import AgencyIDSubtaskRunInfo
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.url.suggestion.agency.suggestion.pydantic import AgencyIDSubtaskSuggestionPydantic


class AgencyIDSubtaskOperatorBase(ABC):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        task_id: int
    ) -> None:
        self.adb_client: AsyncDatabaseClient = adb_client
        self.task_id: int = task_id
        self.linked_urls: list[int] = []

    async def run(self) -> AgencyIDSubtaskRunInfo:
        try:
            await self.inner_logic()
        except Exception as e:
            # Get stack trace
            stack_trace: str = traceback.format_exc()
            return AgencyIDSubtaskRunInfo(
                error=f"{type(e).__name__}: {str(e)}: {stack_trace}",
                linked_url_ids=self.linked_urls
            )
        return AgencyIDSubtaskRunInfo(
            linked_url_ids=self.linked_urls
        )

    @abc.abstractmethod
    async def inner_logic(self) -> AgencyIDSubtaskRunInfo:
        raise NotImplementedError

    async def _upload_subtask_data(
        self,
        subtask_data_list: list[AutoAgencyIDSubtaskData]
    ) -> None:

        subtask_models: list[URLAutoAgencyIDSubtaskPydantic] = [
            subtask_data.pydantic_model
            for subtask_data in subtask_data_list
        ]
        subtask_ids: list[int] = await self.adb_client.bulk_insert(
            models=subtask_models,
            return_ids=True
        )
        suggestions: list[AgencyIDSubtaskSuggestionPydantic] = []
        for subtask_id, subtask_info in zip(subtask_ids, subtask_data_list):
            for suggestion in subtask_info.suggestions:
                suggestion_pydantic = AgencyIDSubtaskSuggestionPydantic(
                    subtask_id=subtask_id,
                    agency_id=suggestion.agency_id,
                    confidence=suggestion.confidence,
                )
                suggestions.append(suggestion_pydantic)

        await self.adb_client.bulk_insert(
            models=suggestions,
        )

        error_infos: list[URLErrorPydanticInfo] = []
        for subtask_info in subtask_data_list:
            if not subtask_info.has_error:
                continue
            error_info = URLErrorPydanticInfo(
                url_id=subtask_info.url_id,
                error=subtask_info.error,
                task_id=self.task_id,
            )
            error_infos.append(error_info)

        await self.adb_client.bulk_insert(
            models=error_infos,
        )
