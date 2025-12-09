import pytest
from fastapi import HTTPException

from src.api.endpoints.submit.data_source.models.response.duplicate import SubmitDataSourceURLDuplicateSubmissionResponse
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_submit_data_source_duplicate(
    api_test_helper: APITestHelper,
    test_agency_id: int,
    pittsburgh_locality: LocalityCreationInfo,
    test_url_data_source_mapping: SimpleURLMapping
):

    ath = api_test_helper
    try:
        ath.request_validator.post_v3(
            url="submit/data-source",
            json=DataSourceSubmissionRequest(
                source_url=test_url_data_source_mapping.url,
                name="Test Name",
                record_type=RecordType.RECORDS_REQUEST_INFO
            ).model_dump(mode='json')
        )
    except HTTPException as e:
        response = e.detail['detail']
        model = SubmitDataSourceURLDuplicateSubmissionResponse(**response)
        assert model.url_id == test_url_data_source_mapping.url_id
        assert model.url_type == URLType.DATA_SOURCE
        assert model.url_status == URLStatus.OK
        assert model.message == "Duplicate URL found"
