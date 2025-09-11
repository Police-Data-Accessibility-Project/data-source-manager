import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.convert import \
    convert_search_agency_responses_to_subtask_data_list
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.mapper import \
    URLRequestIDMapper
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse, \
    SearchAgencyByLocationAgencyInfo
from tests.automated.integration.tasks.url.impl.agency_identification.subtasks.nlp_location_match.internal_processor.convert_search_agency_responses.params import \
    ConvertSearchAgencyResponsesTestParams

PARAMETERS = [
    ConvertSearchAgencyResponsesTestParams(
    search_agency_by_location_responses=[
            SearchAgencyByLocationResponse(
                request_id=1,
                results=[
                    SearchAgencyByLocationAgencyInfo(
                        agency_id=1,
                        similarity=1.0,
                    ),
                    SearchAgencyByLocationAgencyInfo(
                        agency_id=2,
                        similarity=0.5,
                    ),
                ]
            ),
            SearchAgencyByLocationResponse(
                request_id=2,
                results=[
                    SearchAgencyByLocationAgencyInfo(
                        agency_id=3,
                        similarity=0.75,
                    ),
                ]
            )
        ],
        expected_subtask_data=AutoAgencyIDSubtaskData(
            pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                task_id=1,
                url_id=1,
                type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                agencies_found=True,
            ),
            suggestions=[
                AgencySuggestion(
                    agency_id=1,
                    confidence=100,
                ),
                AgencySuggestion(
                    agency_id=2,
                    confidence=50,
                ),
                AgencySuggestion(
                    agency_id=3,
                    confidence=75,
                )
            ]
        )
    ),
    ConvertSearchAgencyResponsesTestParams(
        search_agency_by_location_responses=[
            SearchAgencyByLocationResponse(
                request_id=3,
                results=[
                    SearchAgencyByLocationAgencyInfo(
                        agency_id=1,
                        similarity=1.0,
                    ),
                    SearchAgencyByLocationAgencyInfo(
                        agency_id=2,
                        similarity=0.5,
                    ),
                ]
            )
        ],
        expected_subtask_data=AutoAgencyIDSubtaskData(
            pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                task_id=1,
                url_id=2,
                type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                agencies_found=True,
            ),
            suggestions=[
                AgencySuggestion(
                    agency_id=1,
                    confidence=100,
                ),
                AgencySuggestion(
                    agency_id=2,
                    confidence=50,
                )
            ]
        )
    ),
]

@pytest.mark.asyncio
async def test_params(
) -> None:
    mapper = URLRequestIDMapper()
    mapper.add_mapping(request_id=1, url_id=1)
    mapper.add_mapping(request_id=2, url_id=1)
    mapper.add_mapping(request_id=3, url_id=2)

    search_responses: list[SearchAgencyByLocationResponse] = []
    for param in PARAMETERS:
        search_responses.extend(param.search_agency_by_location_responses)

    subtask_data_list: list[AutoAgencyIDSubtaskData] = \
        convert_search_agency_responses_to_subtask_data_list(
            responses=search_responses,
            task_id=1,
            mapper=mapper,
        )

    assert len(subtask_data_list) == len(PARAMETERS)

    for subtask_data, param in zip(subtask_data_list, PARAMETERS):
        expected_subtask_data: AutoAgencyIDSubtaskData = param.expected_subtask_data
        assert subtask_data.pydantic_model == expected_subtask_data.pydantic_model
        assert subtask_data.suggestions == expected_subtask_data.suggestions

