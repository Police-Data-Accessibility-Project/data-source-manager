from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


class ConvertSearchAgencyResponsesTestParams(BaseModel):
    search_agency_by_location_responses: list[SearchAgencyByLocationResponse]
    expected_subtask_data: AutoAgencyIDSubtaskData
