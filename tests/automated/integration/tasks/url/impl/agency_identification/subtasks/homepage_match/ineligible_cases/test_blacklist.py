import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_blacklist(
    db_data_creator: DBDataCreator,
    operator: AgencyIdentificationTaskOperator,
):
    """Test Survey does not pick up for Homepage Match
    URLs with root URLs that have more than two agencies
     whose meta_urls have it as a root"""
    # Create Root URL
    root_url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Flag as Root
    await db_data_creator.flag_as_root([root_url_id])

    # Create ineligible URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Link Root URL to ineligible URL
    await db_data_creator.link_urls_to_root([url_id], root_url_id=root_url_id)

    # Create Meta URLs
    meta_urls: list[URLMapping] = await db_data_creator.create_validated_urls(
        count=3,
        validation_type=URLType.META_URL
    )

    # Create 3 agencies
    agency_ids: list[int] = await db_data_creator.create_agencies(count=3)

    # Link Meta URLs to Agencies
    await db_data_creator.link_urls_to_agencies(
        url_ids=[url.url_id for url in meta_urls],
        agency_ids=agency_ids
    )

    # Link Meta URLs to Root URL
    await db_data_creator.link_urls_to_root(
        url_ids=[url.url_id for url in meta_urls],
        root_url_id=root_url_id
    )

    # Run survey and confirm prerequisites not met
    assert not await operator.meets_task_prerequisites()
