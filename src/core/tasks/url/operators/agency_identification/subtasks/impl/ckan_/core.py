from typing import final

from typing_extensions import override

from src.core.tasks.url.operators.agency_identification.subtasks.convert import \
    convert_agency_suggestions_to_subtask_data
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan_.params import CKANAgencyIDSubtaskParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan_.query import \
    GetCKANAgencyIDSubtaskParamsQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.core.tasks.url.operators.agency_identification.subtasks.queries.match_agency import MatchAgencyQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import \
    AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.external.pdap.client import PDAPClient


@final
class CKANAgencyIDSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            task_id: int,
            pdap_client: PDAPClient
    ):
        super().__init__(adb_client, task_id=task_id)
        self.pdap_client = pdap_client

    @override
    async def inner_logic(self) -> None:
        params: list[CKANAgencyIDSubtaskParams] = await self._get_params()
        self.linked_urls = [param.url_id for param in params]
        subtask_data_list: list[AutoAgencyIDSubtaskData] = []
        for param in params:
            agency_name: str = param.collector_metadata["agency_name"]
            agency_suggestions: list[AgencySuggestion] = await self.adb_client.run_query_builder(
                MatchAgencyQueryBuilder(
                    agency_name=agency_name
                )
            )
            subtask_data: AutoAgencyIDSubtaskData = convert_agency_suggestions_to_subtask_data(
                url_id=param.url_id,
                agency_suggestions=agency_suggestions,
                subtask_type=AutoAgencyIDSubtaskType.CKAN,
                task_id=self.task_id
            )
            subtask_data_list.append(subtask_data)

        await self._upload_subtask_data(subtask_data_list)

    async def _get_params(self) -> list[CKANAgencyIDSubtaskParams]:
        return await self.adb_client.run_query_builder(
            GetCKANAgencyIDSubtaskParamsQueryBuilder()
        )