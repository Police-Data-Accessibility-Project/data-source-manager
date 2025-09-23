"""
Add DATA SOURCE URL with suggestions aligned in all but record type.
Confirm is not validated until record type tiebreaker is broken
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_record_type(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
):
    raise NotImplementedError