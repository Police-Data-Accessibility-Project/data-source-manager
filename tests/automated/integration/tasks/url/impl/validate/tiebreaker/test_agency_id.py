"""
Add META URL with suggestions aligned in all but agency ID.
Confirm is not validated until agency ID tiebreaker is broken
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator


@pytest.mark.asyncio
async def test_agency_id(
    operator: AutoValidateURLTaskOperator,
):
    raise NotImplementedError