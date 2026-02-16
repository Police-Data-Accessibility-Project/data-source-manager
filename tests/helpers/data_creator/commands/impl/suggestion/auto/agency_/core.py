from typing import final

from typing_extensions import override

from src.core.enums import SuggestionType
from src.db.enums import TaskType
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.annotation.agency.auto.suggestion.pydantic import AgencyIDSubtaskSuggestionPydantic
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.agency import AgencyCommand


@final
class AgencyAutoSuggestionsCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        count: int,
        suggestion_type: SuggestionType = SuggestionType.AUTO_SUGGESTION,
        subtask_type: AutoAgencyIDSubtaskType = AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
        confidence: int = 50
    ):
        super().__init__()
        if suggestion_type == SuggestionType.UNKNOWN:
            count = 1  # Can only be one auto suggestion if unknown
            agencies_found = False
        else:
            agencies_found = True
        self.url_id = url_id
        self.count = count
        self.suggestion_type = suggestion_type
        self.subtask_type = subtask_type
        self.confidence = confidence
        self.agencies_found = agencies_found

    @override
    async def run(self) -> None:
        task_id: int = await self.add_task()
        subtask_id: int = await self.create_subtask(task_id)
        if not self.agencies_found:
            return

        suggestions: list[AgencyIDSubtaskSuggestionPydantic] = []
        for _ in range(self.count):
            pdap_agency_id: int = await self.run_command(AgencyCommand())

            suggestion = AgencyIDSubtaskSuggestionPydantic(
                subtask_id=subtask_id,
                agency_id=pdap_agency_id,
                confidence=self.confidence,
            )
            suggestions.append(suggestion)

        await self.adb_client.bulk_insert(
            models=suggestions,
        )

    async def add_task(self) -> int:
        task_id: int = await self.adb_client.initiate_task(
            task_type=TaskType.AGENCY_IDENTIFICATION,
        )
        return task_id

    async def create_subtask(self, task_id: int) -> int:
        obj: URLAutoAgencyIDSubtaskPydantic = URLAutoAgencyIDSubtaskPydantic(
            task_id=task_id,
            type=self.subtask_type,
            url_id=self.url_id,
            agencies_found=self.agencies_found,
        )
        subtask_id: int = (await self.adb_client.bulk_insert(
            models=[obj],
            return_ids=True
        ))[0]
        return subtask_id

