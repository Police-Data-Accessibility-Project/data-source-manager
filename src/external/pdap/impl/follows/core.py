from pdap_access_manager import AccessManager, DataSourcesNamespaces, RequestInfo, RequestType, ResponseInfo

from src.external.pdap.impl.follows.response import GetFollowsResponse, LinkUserFollow


async def get_user_followed_locations(
    access_manager: AccessManager,
) -> GetFollowsResponse:

    url: str = f"{access_manager.data_sources_url}/v3/v2/source-collector/follows"
    headers: dict[str, str] = await access_manager.jwt_header()
    request_info = RequestInfo(
        type_=RequestType.GET,
        url=url,
        headers=headers
    )
    response_info: ResponseInfo = await access_manager.make_request(request_info)
    return GetFollowsResponse(
        **response_info.data
    )