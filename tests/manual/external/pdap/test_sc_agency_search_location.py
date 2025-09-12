"""

Location ID, Agency ID
10464,9873, "Boonsboro, Washington, Maryland"
15648,9878, "Smithsburg, Washington, Maryland"
15656,9879, "Williamsport, Washington, Maryland"

"""
import pytest

from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


@pytest.mark.asyncio
async def test_sc_agency_search_location(pdap_client_dev: PDAPClient):
    params: list[SearchAgencyByLocationParams] = [
        SearchAgencyByLocationParams(
            request_id=1,
            query="Boonsboro, Washington, Maryland"
        ),
        SearchAgencyByLocationParams(
            request_id=0,
            query="Smithsburg, Washington, Maryland"
        ),
        SearchAgencyByLocationParams(
            request_id=-99,
            query="Williamsport, Washington, Maryland"
        )
    ]
    response: list[SearchAgencyByLocationResponse] = await pdap_client_dev.search_agency_by_location(params)
    print(response)

