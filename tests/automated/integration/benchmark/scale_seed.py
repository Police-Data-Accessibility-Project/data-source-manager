from dataclasses import dataclass

from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.annotation.agency.auto.suggestion.pydantic import AgencyIDSubtaskSuggestionPydantic
from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic
from src.db.models.impl.annotation.location.auto.suggestion.pydantic import LocationIDSubtaskSuggestionPydantic
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.pydantic import URLNameSuggestionPydantic
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.generate import generate_urls, generate_batch_url_links


@dataclass
class ScaleSeedResult:
    api_test_helper: APITestHelper
    url_count: int


async def create_scale_data(
    adb_client: AsyncDatabaseClient,
    db_data_creator: DBDataCreator,
    api_test_helper: APITestHelper,
    url_count: int = 10_000,
) -> ScaleSeedResult:
    """
    Seed the database with url_count URLs plus supporting data so that
    GET /annotate/all exercises the query planner under realistic load.

    All URLs are left unvalidated (not in flag_url_validated) so they appear
    in unvalidated_url_view and are returned by the endpoint on every request.
    No user annotations are created, so all URLs remain eligible each round.

    All expensive steps use bulk inserts — the per-URL helper commands
    (agency_auto_suggestions, add_location_suggestion) each make 4+ DB round-
    trips; at 5k scale that blows through the 300s pytest timeout.  Instead,
    each suggestion type is seeded in exactly 3 round-trips:
        1. initiate_task  (1 row)
        2. bulk_insert subtasks  (N rows, returns IDs)
        3. bulk_insert suggestions  (N rows)
    """

    # 1. Geographic hierarchy — needed before agency-location links
    us_state = await db_data_creator.create_us_state(name="California", iso="CA")
    county_1 = await db_data_creator.create_county(
        state_id=us_state.us_state_id, name="Los Angeles County"
    )
    county_2 = await db_data_creator.create_county(
        state_id=us_state.us_state_id, name="San Francisco County"
    )
    county_3 = await db_data_creator.create_county(
        state_id=us_state.us_state_id, name="Sacramento County"
    )

    counties = [county_1, county_2, county_3]
    locality_location_ids: list[int] = []
    for i in range(10):
        county = counties[i % len(counties)]
        locality = await db_data_creator.create_locality(
            state_id=us_state.us_state_id,
            county_id=county.county_id,
            name=f"Scale City {i}",
        )
        locality_location_ids.append(locality.location_id)

    # 2. 20 agencies linked to localities — makes location-agency joins non-trivial
    agency_ids: list[int] = await db_data_creator.create_agencies(count=20)
    for i, agency_id in enumerate(agency_ids):
        await db_data_creator.link_agencies_to_location(
            agency_ids=[agency_id],
            location_id=locality_location_ids[i % len(locality_location_ids)],
        )

    # 3. 10k URLs — single bulk round-trip, returns all IDs
    urls = generate_urls(count=url_count)
    url_ids: list[int] = await adb_client.bulk_insert(urls, return_ids=True)

    # 4. Batch + links — URLs appear in the standard query context
    batch_id: int = await db_data_creator.create_batch()
    links = generate_batch_url_links(url_ids=url_ids, batch_id=batch_id)
    await adb_client.bulk_insert(links)

    # 5. Name suggestions for 70% of URLs — single bulk insert.
    #    Makes GetNameSuggestionsQueryBuilder non-trivial.
    name_count = int(url_count * 0.7)
    name_suggestions = [
        URLNameSuggestionPydantic(
            url_id=url_id,
            suggestion=f"Scale suggestion {url_id}"[:100],
            source=NameSuggestionSource.HTML_METADATA_TITLE,
        )
        for url_id in url_ids[:name_count]
    ]
    await adb_client.bulk_insert(name_suggestions)

    # 6. Auto agency suggestions for 50% of URLs — 3 bulk round-trips total.
    #    Makes GetAgencySuggestionsQueryBuilder non-trivial.
    agency_subset = url_ids[:int(url_count * 0.5)]
    agency_task_id: int = await adb_client.initiate_task(
        task_type=TaskType.AGENCY_IDENTIFICATION
    )
    agency_subtask_models = [
        URLAutoAgencyIDSubtaskPydantic(
            task_id=agency_task_id,
            url_id=url_id,
            type=AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
            agencies_found=True,
        )
        for url_id in agency_subset
    ]
    agency_subtask_ids: list[int] = await adb_client.bulk_insert(
        agency_subtask_models, return_ids=True
    )
    seed_agency_id = agency_ids[0]
    agency_suggestion_models = [
        AgencyIDSubtaskSuggestionPydantic(
            subtask_id=subtask_id,
            agency_id=seed_agency_id,
            confidence=50,
        )
        for subtask_id in agency_subtask_ids
    ]
    await adb_client.bulk_insert(agency_suggestion_models)

    # 7. Auto location suggestions for 50% of URLs — 3 bulk round-trips total.
    #    Makes GetLocationSuggestionsQueryBuilder non-trivial.
    location_subset = url_ids[:int(url_count * 0.5)]
    location_task_id: int = await adb_client.initiate_task(
        task_type=TaskType.HTML
    )
    primary_location_id = locality_location_ids[0]
    location_subtask_models = [
        AutoLocationIDSubtaskPydantic(
            task_id=location_task_id,
            url_id=url_id,
            type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
            locations_found=True,
        )
        for url_id in location_subset
    ]
    location_subtask_ids: list[int] = await adb_client.bulk_insert(
        location_subtask_models, return_ids=True
    )
    location_suggestion_models = [
        LocationIDSubtaskSuggestionPydantic(
            subtask_id=subtask_id,
            location_id=primary_location_id,
            confidence=0.9,
        )
        for subtask_id in location_subtask_ids
    ]
    await adb_client.bulk_insert(location_suggestion_models)

    return ScaleSeedResult(
        api_test_helper=api_test_helper,
        url_count=url_count,
    )
