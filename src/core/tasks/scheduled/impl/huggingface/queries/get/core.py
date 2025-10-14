from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.huggingface.queries.get.convert import convert_fine_to_coarse_record_type, \
    convert_validated_type_to_relevant
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.db.client.helpers import add_standard_limit_and_offset
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html


class GetForLoadingToHuggingFaceQueryBuilder(QueryBuilderBase):

    def __init__(self, page: int):
        super().__init__()
        self.page = page


    async def run(self, session: AsyncSession) -> list[GetForLoadingToHuggingFaceOutput]:
        label_url_id = 'url_id'
        label_url = 'url'
        label_record_type_fine = 'record_type_fine'
        label_html = 'html'
        label_type = 'type'


        query = (
            select(
                URL.id.label(label_url_id),
                URL.full_url.label(label_url),
                URLRecordType.record_type.label(label_record_type_fine),
                URLCompressedHTML.compressed_html.label(label_html),
                FlagURLValidated.type.label(label_type)
            )
            .join(
                URLRecordType,
                URL.id == URLRecordType.url_id
            )
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .outerjoin(
                FlagURLValidated,
                URL.id == FlagURLValidated.url_id
            )
            .where(
                FlagURLValidated.type.in_(
                    (URLType.DATA_SOURCE,
                     URLType.NOT_RELEVANT)
                )
            )
        )
        query = add_standard_limit_and_offset(page=self.page, statement=query)
        db_results = await sh.mappings(
            session=session,
            query=query
        )
        final_results = []
        for result in db_results:
            output = GetForLoadingToHuggingFaceOutput(
                url_id=result[label_url_id],
                url=result[label_url],
                relevant=convert_validated_type_to_relevant(
                    URLType(result[label_type])
                ),
                record_type_fine=result[label_record_type_fine],
                record_type_coarse=convert_fine_to_coarse_record_type(
                    result[label_record_type_fine]
                ),
                html=decompress_html(result[label_html])
            )
            final_results.append(output)

        return final_results
