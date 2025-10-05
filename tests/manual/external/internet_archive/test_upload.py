import pytest
from aiohttp import ClientSession

from src.external.internet_archives.client import InternetArchivesClient

BASE_URL = "https://www.muckrock.com/foi/allegheny-county-306/policy-documents-170293/"

@pytest.mark.asyncio
async def test_upload():
    """Test basic save requests to the Internet Archive."""

    async with ClientSession() as session:
        client = InternetArchivesClient(session)
        response = await client.save_to_internet_archives(BASE_URL)
        print(response)