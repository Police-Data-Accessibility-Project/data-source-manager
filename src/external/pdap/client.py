from typing import Any

from pdap_access_manager import AccessManager, DataSourcesNamespaces, RequestInfo, RequestType, ResponseInfo

from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.dtos.unique_url_duplicate import UniqueURLDuplicateInfo
from src.external.pdap.enums import MatchAgencyResponseStatus


class PDAPClient:

    def __init__(
        self,
        access_manager: AccessManager,
    ):
        self.access_manager = access_manager

    async def run_request_builder(
        self,
        request_builder: PDAPRequestBuilderBase
    ) -> Any:
        return await request_builder.run(self.access_manager)

    async def match_agency(
        self,
        name: str,
        state: str | None = None,
        county: str | None = None,
        locality: str | None = None
    ) -> MatchAgencyResponse:
        """
        Returns agencies, if any, that match or partially match the search criteria
        """
        url: str = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.MATCH,
            subdomains=["agency"]
        )

        headers: dict[str, str] = await self.access_manager.jwt_header()
        headers['Content-Type']: str = "application/json"
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            headers=headers,
            json_={
                "name": name,
                "state": state,
                "county": county,
                "locality": locality
            }
        )
        response_info: ResponseInfo = await self.access_manager.make_request(request_info)
        matches: list[MatchAgencyInfo] = []
        for agency in response_info.data["agencies"]:
            mai = MatchAgencyInfo(
                id=agency['id'],
                submitted_name=agency['name']
            )
            if len(agency['locations']) > 0:
                first_location: dict[str, Any] = agency['locations'][0]
                mai.state = first_location['state']
                mai.county = first_location['county']
                mai.locality = first_location['locality']
            matches.append(mai)

        return MatchAgencyResponse(
            status=MatchAgencyResponseStatus(response_info.data["status"]),
            matches=matches
        )

    async def is_url_duplicate(
        self,
        url_to_check: str
    ) -> bool:
        """
        Check if a URL is unique. Returns duplicate info otherwise
        """
        url: str = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.CHECK,
            subdomains=["unique-url"]
        )
        request_info = RequestInfo(
            type_=RequestType.GET,
            url=url,
            params={
                "url": url_to_check
            }
        )
        response_info: ResponseInfo = await self.access_manager.make_request(request_info)
        duplicates: list[UniqueURLDuplicateInfo] = [
            UniqueURLDuplicateInfo(**entry) for entry in response_info.data["duplicates"]
        ]
        is_duplicate: bool = (len(duplicates) != 0)
        return is_duplicate
