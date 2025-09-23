"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- URL Type (META URL)
And confirm it is validated as META URL
"""
import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator


@pytest.mark.asyncio
async def test_meta_url(
    operator: AutoValidateURLTaskOperator,
):
    raise NotImplementedError