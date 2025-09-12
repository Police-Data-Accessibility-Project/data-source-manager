from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.api.endpoints.annotate.dtos.record_type.post import RecordTypeAnnotationPostInfo
from src.api.endpoints.annotate.dtos.record_type.response import GetNextRecordTypeAnnotationResponseOuterInfo
from src.core.enums import RecordType
from src.core.error_manager.enums import ErrorTypes
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from tests.automated.integration.api.annotate.helpers import check_url_mappings_match, check_html_info_not_empty, \
    html_info_empty
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_annotate_record_type(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add record type attribute with value `Accident Reports` to 1st URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_1.url_id,
        record_type=RecordType.ACCIDENT_REPORTS
    )

    # Add 'Record Type' attribute with value `Dispatch Recordings` to 2nd URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_2.url_id,
        record_type=RecordType.DISPATCH_RECORDINGS
    )

    # Add HTML data to both
    await ath.db_data_creator.html_data([url_1.url_id, url_2.url_id])

    # Call `GET` `/annotate/record-type` and receive next URL
    request_info_1: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_record_type_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    check_html_info_not_empty(inner_info_1.html_info)

    # Validate that the correct record type is returned
    assert inner_info_1.suggested_record_type == RecordType.ACCIDENT_REPORTS

    # Annotate with value 'Personnel Records' and get next URL
    request_info_2: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.PERSONNEL_RECORDS
        )
    )

    inner_info_2 = request_info_2.next_annotation

    check_url_mappings_match(inner_info_2.url_info, url_2)
    check_html_info_not_empty(inner_info_2.html_info)

    request_info_3: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_2.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.ANNUAL_AND_MONTHLY_REPORTS
        )
    )

    assert request_info_3.next_annotation is None

    # Get all URL annotations. Confirm they exist for user
    adb_client = ath.adb_client()
    results: list[UserRecordTypeSuggestion] = await adb_client.get_all(UserRecordTypeSuggestion)
    result_1 = results[0]
    result_2 = results[1]

    assert result_1.url_id == inner_info_1.url_info.url_id
    assert result_1.record_type == RecordType.PERSONNEL_RECORDS.value

    assert result_2.url_id == inner_info_2.url_info.url_id
    assert result_2.record_type == RecordType.ANNUAL_AND_MONTHLY_REPORTS.value

    # If user submits annotation for same URL, the URL should be overwritten

    request_info_4: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.BOOKING_REPORTS
        )
    )

    assert request_info_4.next_annotation is None

    results: list[UserRecordTypeSuggestion] = await adb_client.get_all(UserRecordTypeSuggestion)
    assert len(results) == 2

    for result in results:
        if result.url_id == inner_info_1.url_info.url_id:
            assert result.record_type == RecordType.BOOKING_REPORTS.value


@pytest.mark.asyncio
async def test_annotate_record_type_already_annotated_by_different_user(
        api_test_helper
):
    ath = api_test_helper

    creation_info: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1
    )

    await ath.db_data_creator.user_record_type_suggestion(
        url_id=creation_info.url_ids[0],
        user_id=2,
        record_type=RecordType.ACCIDENT_REPORTS
    )

    # Annotate with different user (default is 1) and get conflict error
    try:
        response = await ath.request_validator.post_record_type_annotation_and_get_next(
            url_id=creation_info.url_ids[0],
            record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
                record_type=RecordType.ANNUAL_AND_MONTHLY_REPORTS
            )
        )
    except HTTPException as e:
        assert e.status_code == HTTPStatus.CONFLICT
        assert e.detail["detail"]["code"] == ErrorTypes.ANNOTATION_EXISTS.value
        assert e.detail["detail"]["message"] == f"Annotation of type RECORD_TYPE already exists for url {creation_info.url_ids[0]}"


@pytest.mark.asyncio
async def test_annotate_record_type_no_html_info(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add record type attribute with value `Accident Reports` to 1st URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_1.url_id,
        record_type=RecordType.ACCIDENT_REPORTS
    )

    # Add 'Record Type' attribute with value `Dispatch Recordings` to 2nd URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_2.url_id,
        record_type=RecordType.DISPATCH_RECORDINGS
    )

    # Call `GET` `/annotate/record-type` and receive next URL
    request_info_1: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_record_type_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    assert html_info_empty(inner_info_1.html_info)
