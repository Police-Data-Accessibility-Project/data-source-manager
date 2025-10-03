from typing import Any

from pdap_access_manager import AccessManager, DataSourcesNamespaces, RequestInfo, RequestType, ResponseInfo

from src.external.pdap.impl.meta_urls.enums import SubmitMetaURLsStatus
from src.external.pdap.impl.meta_urls.request import SubmitMetaURLsRequest
from src.external.pdap.impl.meta_urls.response import SubmitMetaURLsResponse


async def submit_meta_urls(
    access_manager: AccessManager,
    requests: list[SubmitMetaURLsRequest]
) -> list[SubmitMetaURLsResponse]:


    # Build url-id dictionary
    url_id_dict: dict[str, int] = {}
    for request in requests:
        url_id_dict[request.url] = request.url_id

    meta_urls_json: list[dict[str, Any]] = []
    for request in requests:
        meta_urls_json.append(
            {
                "url": request.url,
                "agency_id": request.agency_id
            }
        )

    headers: dict[str, str] = await access_manager.jwt_header()
    url: str = access_manager.build_url(
        namespace=DataSourcesNamespaces.SOURCE_COLLECTOR,
        subdomains=["meta-urls"]
    )
    request_info = RequestInfo(
        type_=RequestType.POST,
        url=url,
        headers=headers,
        json_={
            "data_sources": meta_urls_json
        }
    )

    response_info: ResponseInfo = await access_manager.make_request(request_info)
    meta_urls_response_json: list[dict[str, Any]] = response_info.data["meta_urls"]

    responses: list[SubmitMetaURLsResponse] = []
    for meta_url in meta_urls_response_json:
        responses.append(
            SubmitMetaURLsResponse(
                url=meta_url["url"],
                status=SubmitMetaURLsStatus(meta_url["status"]),
                agency_id=meta_url["agency_id"],
                meta_url_id=meta_url["meta_url_id"],
                error=meta_url["error"]
            )
        )
    return responses