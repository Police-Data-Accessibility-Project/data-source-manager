# TODO: Add URL with 2 INDIVIDUAL RECORD suggestions. Check validated as INDIVIDUAL RECORD
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator


@pytest.mark.asyncio
async def test_individual_record(
    operator: AutoValidateURLTaskOperator,
):
    raise NotImplementedError