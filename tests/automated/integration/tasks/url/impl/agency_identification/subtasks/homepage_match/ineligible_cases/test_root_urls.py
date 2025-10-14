import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from tests.conftest import db_data_creator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_root_urls(
    db_data_creator: DBDataCreator,
    operator: AgencyIdentificationTaskOperator,
):
    """Test survey does not pick up root URLs for Homepage Match."""

    # Create URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Flag as Root
    await db_data_creator.flag_as_root([url_id])

    # Run survey and confirm prerequisites not met
    assert not await operator.meets_task_prerequisites()