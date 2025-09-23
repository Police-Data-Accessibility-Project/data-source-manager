
"""
Add URL with two suggestions for both
- NOT RELEVANT
- INDIVIDUAL RECORD
And confirm it is not validated
Then add an additional NOT RELEVANT suggestion and confirm it is validated as NOT RELEVANT
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator


@pytest.mark.asyncio
async def test_url_type(
    operator: AutoValidateURLTaskOperator,
):
    raise NotImplementedError