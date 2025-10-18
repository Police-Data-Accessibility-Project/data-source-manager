from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.insert_redirects.extract import extract_response_pairs
from src.core.tasks.url.operators.probe.queries.insert_redirects.request_manager import InsertRedirectsRequestManager
from src.core.tasks.url.operators.probe.queries.urls.exist.model import URLExistsResult
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping_.full import FullURLMapping
from src.db.queries.base.builder import QueryBuilderBase
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.models.full_url import FullURL
from src.util.url_mapper_.full import FullURLMapper


class InsertRedirectsQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        tdos: list[URLProbeTDO],
    ):
        super().__init__()
        self.tdos = tdos
        self.source_url_mappings = [tdo.url_mapping for tdo in self.tdos]
        self._mapper = FullURLMapper(self.source_url_mappings)

        self._response_pairs: list[URLProbeRedirectResponsePair] = extract_response_pairs(self.tdos)

        self._destination_probe_responses: list[URLProbeResponse] = [
            pair.destination
            for pair in self._response_pairs
        ]
        self._destination_urls: list[FullURL] = [
            response.url
            for response in self._destination_probe_responses
        ]

        self._destination_url_to_probe_response_mapping: dict[FullURL, URLProbeResponse] = {
            response.url: response
            for response in self._destination_probe_responses
        }




    async def run(self, session: AsyncSession) -> None:
        """
        Modifies:
            self._mapper
        """

        rm = InsertRedirectsRequestManager(
            session=session
        )

        # Get all destination URLs already in the database
        url_exist_results: list[URLExistsResult] = await rm.check_if_urls_exist_in_db(
            urls=self._destination_urls
        )

        # Two Options:
        #  - URLs that do not exist in any form in the database
        #  - URLs that exist as-is or in slightly modified version (url scheme or trailing slash differs)
        new_urls: list[FullURL] = []
        extant_url_mappings: list[FullURLMapping] = []
        for result in url_exist_results:
            if not result.exists:
                new_urls.append(result.query_url)
            else:
                extant_url_mappings.append(
                    FullURLMapping(
                        full_url=result.query_url,
                        url_id=result.url_id
                    )
                )

        # Add the new URLs
        new_dest_url_mappings: list[FullURLMapping] = await rm.insert_new_urls(
            urls=new_urls
        )

        all_url_mappings: list[FullURLMapping] = extant_url_mappings + new_dest_url_mappings

        self._mapper.add_mappings(all_url_mappings)

        # Add web metadata for new URLs
        await rm.add_web_metadata(
            all_dest_url_mappings=all_url_mappings,
            dest_url_to_probe_response_mappings=self._destination_url_to_probe_response_mapping,
            tdos=self.tdos
        )

        # Add redirect links for new URLs
        await rm.add_redirect_links(
            response_pairs=self._response_pairs,
            mapper=self._mapper
        )
