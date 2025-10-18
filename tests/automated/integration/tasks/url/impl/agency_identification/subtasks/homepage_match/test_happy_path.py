from collections import defaultdict

import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_homepage_match(
    db_data_creator: DBDataCreator,
    operator: AgencyIdentificationTaskOperator,
):
    """
    Test the following cases:
    Single Agency: A URL whose Root URL has one meta URL is properly linked
    Multi Agency: A URL whose Root URL has multiple meta URLs is properly linked
    """

    # Create 2 root URLs
    root_url_mappings: list[SimpleURLMapping] = (
        await db_data_creator.create_urls(count=2)
    )
    root_url_ids: list[int] = [url_mapping.url_id for url_mapping in root_url_mappings]

    # Flag as Root
    await db_data_creator.flag_as_root(root_url_ids)

    # Separate Root URLs
    single_agency_root_url_id: int = root_url_ids[0]
    multi_agency_root_url_id: int = root_url_ids[1]

    # Create 3 agencies
    agency_ids: list[int] = await db_data_creator.create_agencies(count=3)
    single_agency_id: int = agency_ids[0]
    multi_agency_ids: list[int] = agency_ids[1:]

    # Create 1 Meta URL for single agency case
    single_meta_url_id: int = (await db_data_creator.create_validated_urls(
        count=1,
        validation_type=URLType.META_URL
    ))[0].url_id
    # Link single meta URL to single agency
    await db_data_creator.create_url_agency_links(
        url_ids=[single_meta_url_id],
        agency_ids=[single_agency_id])
    # Link single meta URL to root
    await db_data_creator.link_urls_to_root(
        url_ids=[single_meta_url_id],
        root_url_id=single_agency_root_url_id
    )


    # Create 2 Meta URLs and agencies for multi agency case
    multi_meta_urls: list[SimpleURLMapping] = await db_data_creator.create_validated_urls(
        count=2,
        validation_type=URLType.META_URL
    )
    multi_meta_url_ids: list[int] = [url_mapping.url_id for url_mapping in multi_meta_urls]
    # Link multi meta URLs to agencies
    await db_data_creator.create_url_agency_links(
        url_ids=[multi_meta_url_ids[0]],
        agency_ids=[multi_agency_ids[0]]
    )
    await db_data_creator.create_url_agency_links(
        url_ids=[multi_meta_url_ids[1]],
        agency_ids=[multi_agency_ids[1]]
    )
    # Link multi meta URLs to root
    await db_data_creator.link_urls_to_root(
        url_ids=multi_meta_url_ids,
        root_url_id=multi_agency_root_url_id
    )

    # Check operator does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Set up eligible URLs
    eligible_urls: list[SimpleURLMapping] = await db_data_creator.create_urls(
        count=2,
    )
    single_url_id: int = eligible_urls[0].url_id
    multi_url_id: int = eligible_urls[1].url_id

    # Link eligible URLs to each root
    await db_data_creator.link_urls_to_root(
        url_ids=[single_url_id],
        root_url_id=single_agency_root_url_id
    )
    await db_data_creator.link_urls_to_root(
        url_ids=[multi_url_id],
        root_url_id=multi_agency_root_url_id
    )

    # Check operator now meets prerequisites
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.HOMEPAGE_MATCH

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    adb_client: AsyncDatabaseClient = db_data_creator.adb_client

    # Confirm presence of subtasks
    subtasks: list[URLAutoAgencyIDSubtask] = await adb_client.get_all(URLAutoAgencyIDSubtask)
    assert len(subtasks) == 2

    # Confirm both listed as agencies found
    assert all(subtask.agencies_found for subtask in subtasks)

    url_id_to_subtask: dict[int, URLAutoAgencyIDSubtask] = {
        subtask.url_id: subtask for subtask in subtasks
    }
    single_subtask: URLAutoAgencyIDSubtask = url_id_to_subtask[single_url_id]
    multi_subtask: URLAutoAgencyIDSubtask = url_id_to_subtask[multi_url_id]

    # Check subtasks have expected detail codes
    assert single_subtask.detail == SubtaskDetailCode.HOMEPAGE_SINGLE_AGENCY
    assert multi_subtask.detail == SubtaskDetailCode.HOMEPAGE_MULTI_AGENCY


    # Get suggestions
    suggestions: list[AgencyIDSubtaskSuggestion] = await adb_client.get_all(AgencyIDSubtaskSuggestion)
    assert len(suggestions) == 3

    # Confirm each suggestion properly linked to expected subtask
    subtask_id_to_suggestions: dict[int, list[AgencyIDSubtaskSuggestion]] = defaultdict(list)
    for suggestion in suggestions:
        subtask_id_to_suggestions[suggestion.subtask_id].append(suggestion)

    # Check Single Agency Case Suggestion
    single_suggestion: AgencyIDSubtaskSuggestion = \
        subtask_id_to_suggestions[single_subtask.id][0]
    # Check Single Agency Case Suggestion has expected agency
    assert single_suggestion.agency_id == single_agency_id
    # Confirm confidence is 95
    assert single_suggestion.confidence == 95

    # Check Multi Agency Case Suggestion
    multi_suggestions: list[AgencyIDSubtaskSuggestion] = subtask_id_to_suggestions[multi_subtask.id]
    # Check Multi Agency Case Suggestion has expected agencies
    assert {suggestion.agency_id for suggestion in multi_suggestions} \
        == set(multi_agency_ids)
    # Confirm confidence for each is 50
    assert all(suggestion.confidence == 50 for suggestion in multi_suggestions)

    # Test operator no longer meets prerequisites
    assert not await operator.meets_task_prerequisites()