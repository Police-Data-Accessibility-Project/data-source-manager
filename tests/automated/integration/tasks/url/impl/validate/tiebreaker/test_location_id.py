"""
Add META URL with suggestions aligned in all but location ID.
Confirm is not validated until location ID tiebreaker is broken
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_location_id(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
):
    raise NotImplementedError