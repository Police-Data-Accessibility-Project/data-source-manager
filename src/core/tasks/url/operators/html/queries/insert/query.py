from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.html.queries.insert.convert import convert_to_compressed_html, \
    convert_to_html_content_info_list, convert_to_scrape_infos, convert_to_url_errors
from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.models.impl.url.html.compressed.pydantic import URLCompressedHTMLPydantic
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.impl.url.scrape_info.pydantic import URLScrapeInfoInsertModel
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class InsertURLHTMLInfoQueryBuilder(QueryBuilderBase):

    def __init__(self, tdos: list[UrlHtmlTDO], task_id: int):
        super().__init__()
        self.tdos = tdos
        self.task_id = task_id

    async def run(self, session: AsyncSession) -> None:
        compressed_html_models: list[URLCompressedHTMLPydantic] = convert_to_compressed_html(self.tdos)
        url_html_content_list: list[URLHTMLContent] = convert_to_html_content_info_list(self.tdos)
        scrape_info_list: list[URLScrapeInfoInsertModel] = convert_to_scrape_infos(self.tdos)
        url_errors = convert_to_url_errors(self.tdos, task_id=self.task_id)

        for models in [
            compressed_html_models,
            scrape_info_list,
            url_errors
        ]:
            await sh.bulk_insert(session, models=models)

        await sh.add_all(session=session, models=url_html_content_list)




