from typing import Sequence

from sqlalchemy import select, tuple_, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.insert_redirects.convert import convert_to_url_insert_models, \
    convert_tdo_to_url_response_mappings, \
    convert_url_response_mapping_to_web_metadata_list
from src.core.tasks.url.operators.probe.queries.insert_redirects.map import map_url_mappings_to_probe_responses
from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.db.queries.urls_exist.model import URLExistsResult
from src.db.queries.urls_exist import URLsExistInDBQueryBuilder
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping_.full import FullURLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.url_redirect_url.pydantic import LinkURLRedirectURLPydantic
from src.db.models.impl.link.url_redirect_url.sqlalchemy import LinkURLRedirectURL
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.models.full_url import FullURL
from src.util.url_mapper_.full import FullURLMapper


class InsertRedirectsRequestManager:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_if_urls_exist_in_db(
        self,
        urls: list[FullURL],
    ) -> list[URLExistsResult]:
        results: list[URLExistsResult] = await URLsExistInDBQueryBuilder(
            full_urls=urls
        ).run(self.session)
        return results

    async def insert_new_urls(self, urls: list[FullURL]) -> list[FullURLMapping]:
        if len(urls) == 0:
            return []
        deduplicated_urls = list(set(urls))
        insert_models = convert_to_url_insert_models(deduplicated_urls)
        url_ids = await sh.bulk_insert(self.session, models=insert_models, return_ids=True)
        url_mappings = [
            FullURLMapping(full_url=url, url_id=url_id)
            for url, url_id
            in zip(deduplicated_urls, url_ids)
        ]
        return url_mappings

    async def add_web_metadata(
        self,
        all_dest_url_mappings: list[FullURLMapping],
        dest_url_to_probe_response_mappings: dict[FullURL, URLProbeResponse],
        tdos: list[URLProbeTDO],
    ) -> None:
        dest_url_response_mappings = map_url_mappings_to_probe_responses(
            url_mappings=all_dest_url_mappings,
            url_to_probe_responses=dest_url_to_probe_response_mappings
        )
        src_url_response_mappings: list[URLResponseMapping] = convert_tdo_to_url_response_mappings(
            tdos=tdos
        )
        all_url_response_mappings: list[URLResponseMapping] = src_url_response_mappings + dest_url_response_mappings
        web_metadata_list: list[URLWebMetadataPydantic] = convert_url_response_mapping_to_web_metadata_list(
            all_url_response_mappings
        )
        await sh.bulk_upsert(self.session, models=web_metadata_list)

    async def add_redirect_links(
        self,
        response_pairs: list[URLProbeRedirectResponsePair],
        mapper: FullURLMapper
    ) -> None:
        # Get all existing links and exclude
        link_tuples: list[tuple[int, int]] = []
        for pair in response_pairs:
            source_url_id = mapper.get_id(pair.source.url)
            destination_url_id = mapper.get_id(pair.destination.url)
            link_tuples.append((source_url_id, destination_url_id))

        query = (
            select(
                LinkURLRedirectURL.source_url_id,
                LinkURLRedirectURL.destination_url_id
            )
            .where(
                tuple_(
                    LinkURLRedirectURL.source_url_id,
                    LinkURLRedirectURL.destination_url_id
                ).in_(link_tuples)
            )
        )
        mappings: Sequence[RowMapping] = await sh.mappings(self.session, query=query)
        existing_links: set[tuple[int, int]] = {
            (mapping["source_url_id"], mapping["destination_url_id"])
            for mapping in mappings
        }
        new_links: list[tuple[int, int]] = [
            (source_url_id, destination_url_id)
            for source_url_id, destination_url_id in link_tuples
            if (source_url_id, destination_url_id) not in existing_links
        ]


        links: list[LinkURLRedirectURLPydantic] = []
        for link in new_links:
            source_url_id, destination_url_id = link
            link = LinkURLRedirectURLPydantic(
                source_url_id=source_url_id,
                destination_url_id=destination_url_id
            )
            links.append(link)
        await sh.bulk_insert(self.session, models=links)
