
import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_no_validated_meta_urls(
    db_data_creator: DBDataCreator,
    operator: AgencyIdentificationTaskOperator,
):
    """Test survey does not pick up for Homepage Match
    URLs whose Root URLs do not have validated meta URLs."""

    # Create Root URL
    root_url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Flag as Root
    await db_data_creator.flag_as_root([root_url_id])

    # Create ineligible URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Link Root URL to ineligible URL
    await db_data_creator.link_urls_to_root([url_id], root_url_id=root_url_id)

    # Run survey and confirm prerequisites not met
    assert not await operator.meets_task_prerequisites()