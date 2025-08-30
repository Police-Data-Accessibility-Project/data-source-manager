import pytest


@pytest.mark.asyncio
async def test_validated_meta_url_not_included():
    """
    If a validated Meta URL is included in the database
    This should not be included in the submit approved task
    """
    raise NotImplementedError