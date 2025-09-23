# TODO: Add URL with 2 INDIVIDUAL RECORD suggestions. Check validated as INDIVIDUAL RECORD
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_individual_record(
    operator: AutoValidateURLTaskOperator,
    db_data_creator: DBDataCreator,
):
    raise NotImplementedError