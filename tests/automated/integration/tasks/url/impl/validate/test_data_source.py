"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- Record Type
- URL Type (DATA SOURCE)
And confirm it is validated as DATA SOURCE
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator


@pytest.mark.asyncio
async def test_data_source(
    operator: AutoValidateURLTaskOperator,
):
    raise NotImplementedError