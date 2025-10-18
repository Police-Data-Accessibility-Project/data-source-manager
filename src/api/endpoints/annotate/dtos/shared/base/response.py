from pydantic import BaseModel, Field

from src.api.endpoints.annotate.dtos.shared.batch import AnnotationBatchInfo
from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.db.dtos.url.mapping_.simple import SimpleURLMapping


class AnnotationInnerResponseInfoBase(BaseModel):
    url_info: SimpleURLMapping = Field(
        title="Information about the URL"
    )
    html_info: ResponseHTMLInfo = Field(
        title="HTML information about the URL"
    )
    batch_info: AnnotationBatchInfo | None = Field(
        title="Information about the annotation batch"
    )