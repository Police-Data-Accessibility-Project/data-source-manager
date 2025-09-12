from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.api.endpoints.annotate.relevance.get.dto import GetNextRelevanceAnnotationResponseOuterInfo
from src.api.endpoints.annotate.relevance.post.dto import RelevanceAnnotationPostInfo
from src.core.enums import SuggestedStatus
from src.core.error_manager.enums import ErrorTypes
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion
from tests.automated.integration.api.annotate.helpers import check_url_mappings_match, check_html_info_not_empty, \
    html_info_empty
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_annotate_relevancy(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add `Relevancy` attribute with value `True` to 1st URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    # Add 'Relevancy' attribute with value `False` to 2nd URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_2.url_id,
        relevant=False
    )

    # Add HTML data to both
    await ath.db_data_creator.html_data([url_1.url_id, url_2.url_id])
    # Call `GET` `/annotate/relevance` and receive next URL
    request_info_1: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_relevance_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    check_html_info_not_empty(inner_info_1.html_info)

    # Validate that the correct relevant value is returned
    assert inner_info_1.annotation.is_relevant is True

    # A second user should see the same URL


    #  Annotate with value 'False' and get next URL
    request_info_2: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            suggested_status=SuggestedStatus.NOT_RELEVANT
        )
    )

    inner_info_2 = request_info_2.next_annotation

    check_url_mappings_match(
        inner_info_2.url_info,
        url_2
    )
    check_html_info_not_empty(inner_info_2.html_info)

    request_info_3: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_2.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            suggested_status=SuggestedStatus.RELEVANT
        )
    )

    assert request_info_3.next_annotation is None

    # Get all URL annotations. Confirm they exist for user
    adb_client = ath.adb_client()
    results: list[UserRelevantSuggestion] = await adb_client.get_all(UserRelevantSuggestion)
    result_1 = results[0]
    result_2 = results[1]

    assert result_1.url_id == inner_info_1.url_info.url_id
    assert result_1.suggested_status == SuggestedStatus.NOT_RELEVANT.value

    assert result_2.url_id == inner_info_2.url_info.url_id
    assert result_2.suggested_status == SuggestedStatus.RELEVANT.value

    # If user submits annotation for same URL, the URL should be overwritten
    request_info_4: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            suggested_status=SuggestedStatus.RELEVANT
        )
    )

    assert request_info_4.next_annotation is None

    results: list[UserRelevantSuggestion] = await adb_client.get_all(UserRelevantSuggestion)
    assert len(results) == 2

    for result in results:
        if result.url_id == inner_info_1.url_info.url_id:
            assert results[0].suggested_status == SuggestedStatus.RELEVANT.value


async def post_and_validate_relevancy_annotation(ath, url_id, annotation: SuggestedStatus):
    response = ath.request_validator.post_relevance_annotation_and_get_next(
        url_id=url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            suggested_status=annotation
        )
    )

    assert response.next_annotation is None

    results: list[UserRelevantSuggestion] = await ath.adb_client().get_all(UserRelevantSuggestion)
    assert len(results) == 1
    assert results[0].suggested_status == annotation.value


@pytest.mark.asyncio
async def test_annotate_relevancy_broken_page(api_test_helper):
    ath = api_test_helper

    creation_info = await ath.db_data_creator.batch_and_urls(url_count=1, with_html_content=False)

    await post_and_validate_relevancy_annotation(
        ath,
        url_id=creation_info.url_ids[0],
        annotation=SuggestedStatus.BROKEN_PAGE_404
    )


@pytest.mark.asyncio
async def test_annotate_relevancy_individual_record(api_test_helper):
    ath = api_test_helper

    creation_info: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1
    )

    await post_and_validate_relevancy_annotation(
        ath,
        url_id=creation_info.url_ids[0],
        annotation=SuggestedStatus.INDIVIDUAL_RECORD
    )


@pytest.mark.asyncio
async def test_annotate_relevancy_already_annotated_by_different_user(
        api_test_helper
):
    ath = api_test_helper

    creation_info: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1
    )

    await ath.db_data_creator.user_relevant_suggestion(
        url_id=creation_info.url_ids[0],
        user_id=2,
        suggested_status=SuggestedStatus.RELEVANT
    )

    # Annotate with different user (default is 1) and get conflict error
    try:
        response = await ath.request_validator.post_relevance_annotation_and_get_next(
            url_id=creation_info.url_ids[0],
            relevance_annotation_post_info=RelevanceAnnotationPostInfo(
                suggested_status=SuggestedStatus.NOT_RELEVANT
            )
        )
    except HTTPException as e:
        assert e.status_code == HTTPStatus.CONFLICT
        assert e.detail["detail"]["code"] == ErrorTypes.ANNOTATION_EXISTS.value
        assert e.detail["detail"]["message"] == f"Annotation of type RELEVANCE already exists for url {creation_info.url_ids[0]}"


@pytest.mark.asyncio
async def test_annotate_relevancy_no_html(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add `Relevancy` attribute with value `True` to 1st URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    # Add 'Relevancy' attribute with value `False` to 2nd URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_2.url_id,
        relevant=False
    )

    # Call `GET` `/annotate/relevance` and receive next URL
    request_info_1: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_relevance_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    assert html_info_empty(inner_info_1.html_info)
