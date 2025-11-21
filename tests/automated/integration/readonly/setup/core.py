from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.automated.integration.readonly.setup.agency import add_agency
from tests.automated.integration.readonly.setup.annotations import add_full_data_sources_annotations, \
    add_minimal_not_relevant_annotation
from tests.automated.integration.readonly.setup.data_source import add_maximal_data_source, add_minimal_data_source
from tests.automated.integration.readonly.setup.meta_url import add_meta_url
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


async def setup_readonly_data(
    api_test_helper: APITestHelper
) -> ReadOnlyTestHelper:
    db_data_creator = api_test_helper.db_data_creator
    adb_client = db_data_creator.adb_client

    # Pennsylvania
    pennsylvania: USStateCreationInfo = await db_data_creator.create_us_state(
        name="Pennsylvania",
        iso="PA"
    )
    allegheny_county: CountyCreationInfo = await db_data_creator.create_county(
        state_id=pennsylvania.us_state_id,
        name="Allegheny"
    )
    pittsburgh: LocalityCreationInfo = await db_data_creator.create_locality(
        state_id=pennsylvania.us_state_id,
        county_id=allegheny_county.county_id,
        name="Pittsburgh"
    )

    # Add Agencies
    agency_1_id: int = await add_agency(adb_client, pittsburgh.location_id)
    agency_2_id: int = await add_agency(adb_client, allegheny_county.location_id)


    # Add users with varying contributions
    user_id_1: int = 1
    user_id_2: int = 2
    # Add unvalidated URL
    unvalidated_url_id: int = (await db_data_creator.create_urls(
        record_type=None,
        count=1
    ))[0].url_id
    # Have User 1 give a full set of data sources annotations
    await add_full_data_sources_annotations(
        url_id=unvalidated_url_id,
        user_id=user_id_1,
        agency_id=agency_1_id,
        location_id=pittsburgh.location_id,
        adb_client=adb_client
    )
    # Have User 2 give a single rejected annotation
    await add_minimal_not_relevant_annotation(
        url_id=unvalidated_url_id,
        user_id=user_id_2,
        adb_client=adb_client
    )

    # Add Data Source With Linked Agency
    maximal_data_source: int = await add_maximal_data_source(
        agency_1_id=agency_1_id,
        db_data_creator=db_data_creator
    )
    minimal_data_source: int = await add_minimal_data_source(
        agency_1_id=agency_1_id,
        db_data_creator=db_data_creator
    )

    # Add Meta URL with Linked Agency
    url_meta_url_id: int = await add_meta_url(agency_1_id, db_data_creator)

    return ReadOnlyTestHelper(
        adb_client=adb_client,
        api_test_helper=api_test_helper,

        # Agencies
        agency_1_id=agency_1_id,
        agency_1_location_id=pittsburgh.location_id,
        agency_2_id=agency_2_id,
        agency_2_location_id=allegheny_county.location_id,

        # URLs
        maximal_data_source_url_id=maximal_data_source,
        minimal_data_source_url_id=minimal_data_source,
        url_meta_url_id=url_meta_url_id,
        unvalidated_url_id=unvalidated_url_id,

        # Users
        user_1_id=user_id_1,
        user_2_id=user_id_2,
    )


