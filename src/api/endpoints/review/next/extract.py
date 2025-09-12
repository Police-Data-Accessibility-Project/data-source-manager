from src.api.endpoints.review.next.dto import FinalReviewOptionalMetadata
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.models.impl.url.core.sqlalchemy import URL


async def extract_html_content_infos(
    url: URL
)-> list[URLHTMLContentInfo]:
    html_content = url.html_content
    html_content_infos = [
        URLHTMLContentInfo(**html_info.__dict__)
        for html_info in html_content
    ]
    return html_content_infos

async def extract_optional_metadata(url: URL) -> FinalReviewOptionalMetadata:
    if url.optional_data_source_metadata is None:
        return FinalReviewOptionalMetadata()
    return FinalReviewOptionalMetadata(
        record_formats=url.optional_data_source_metadata.record_formats,
        data_portal_type=url.optional_data_source_metadata.data_portal_type,
        supplying_entity=url.optional_data_source_metadata.supplying_entity
    )