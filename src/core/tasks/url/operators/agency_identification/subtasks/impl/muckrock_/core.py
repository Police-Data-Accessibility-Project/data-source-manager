from typing import final

from typing_extensions import override

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.impl.muckrock.enums import AgencyLookupResponseType
from src.core.tasks.url.operators.agency_identification.subtasks.convert import \
    convert_match_agency_response_to_subtask_data
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock_.params import \
    MuckrockAgencyIDSubtaskParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock_.query import \
    GetMuckrockAgencyIDSubtaskParamsQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse


@final
class MuckrockAgencyIDSubtaskOperator(AgencyIDSubtaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            task_id: int,
            muckrock_api_interface: MuckrockAPIInterface,
            pdap_client: PDAPClient
    ):
        super().__init__(adb_client, task_id=task_id)
        self.muckrock_api_interface = muckrock_api_interface
        self.pdap_client = pdap_client

    @override
    async def inner_logic(self) -> None:
        params: list[MuckrockAgencyIDSubtaskParams] = await self._get_params()
        self.linked_urls = [param.url_id for param in params]
        subtask_data_list: list[AutoAgencyIDSubtaskData] = []
        for param in params:
            muckrock_agency_id: int = param.collector_metadata["agency"]
            agency_lookup_response: AgencyLookupResponse = await self.muckrock_api_interface.lookup_agency(
                muckrock_agency_id=muckrock_agency_id
            )
            if agency_lookup_response.type != AgencyLookupResponseType.FOUND:
                data: AutoAgencyIDSubtaskData = await self._error_subtask_data(
                    url_id=param.url_id,
                    muckrock_agency_id=muckrock_agency_id,
                    agency_lookup_response=agency_lookup_response
                )
                subtask_data_list.append(data)
                continue
            match_agency_response: MatchAgencyResponse = await self.pdap_client.match_agency(
                name=agency_lookup_response.name
            )
            subtask_data: AutoAgencyIDSubtaskData = convert_match_agency_response_to_subtask_data(
                url_id=param.url_id,
                response=match_agency_response,
                subtask_type=AutoAgencyIDSubtaskType.MUCKROCK,
                task_id=self.task_id
            )
            subtask_data_list.append(subtask_data)

        await self._upload_subtask_data(subtask_data_list)


    async def _error_subtask_data(
        self,
        url_id: int,
        muckrock_agency_id: int,
        agency_lookup_response: AgencyLookupResponse
    ) -> AutoAgencyIDSubtaskData:
        pydantic_model = URLAutoAgencyIDSubtaskPydantic(
            task_id=self.task_id,
            url_id=url_id,
            type=AutoAgencyIDSubtaskType.MUCKROCK,
            agencies_found=False,
            detail=SubtaskDetailCode.RETRIEVAL_ERROR
        )
        error: str = f"Failed to lookup muckrock agency: {muckrock_agency_id}:" + \
            f" {agency_lookup_response.type.value}: {agency_lookup_response.error}"
        return AutoAgencyIDSubtaskData(
            pydantic_model=pydantic_model,
            suggestions=[],
            error=error
        )

    async def _get_params(self) -> list[MuckrockAgencyIDSubtaskParams]:
        return await self.adb_client.run_query_builder(
            GetMuckrockAgencyIDSubtaskParamsQueryBuilder()
        )