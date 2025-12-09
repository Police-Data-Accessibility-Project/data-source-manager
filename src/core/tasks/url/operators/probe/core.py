from typing import final

from typing_extensions import override

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.probe.convert import convert_tdo_to_web_metadata_list, \
    convert_tdos_with_functional_equivalents_to_web_metadata_list
from src.core.tasks.url.operators.probe.filter import filter_non_redirect_tdos, filter_redirect_tdos, \
    filter_functionally_equivalent_urls
from src.core.tasks.url.operators.probe.models.subsets import RedirectTDOSubsets
from src.core.tasks.url.operators.probe.models.upsert_functional_equivalents import URLFunctionalEquivalentsUpsertModel
from src.core.tasks.url.operators.probe.queries.insert_redirects.query import InsertRedirectsQueryBuilder
from src.core.tasks.url.operators.probe.queries.urls.not_probed.exists import HasURLsWithoutProbeQueryBuilder
from src.core.tasks.url.operators.probe.queries.urls.not_probed.get.query import GetURLsWithoutProbeQueryBuilder
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping_.full import FullURLMapping
from src.db.enums import TaskType
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from src.external.url_request.core import URLRequestInterface


@final
class URLProbeTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        url_request_interface: URLRequestInterface
    ):
        super().__init__(adb_client=adb_client)
        self.url_request_interface = url_request_interface


    @property
    @override
    def task_type(self) -> TaskType:
        return TaskType.PROBE_URL

    @override
    async def meets_task_prerequisites(self) -> bool:
        return await self.has_urls_without_probe()

    async def get_urls_without_probe(self) -> list[URLProbeTDO]:
        url_mappings: list[FullURLMapping] = await self.adb_client.run_query_builder(
            GetURLsWithoutProbeQueryBuilder()
        )
        return [URLProbeTDO(url_mapping=url_mapping) for url_mapping in url_mappings]

    @override
    async def inner_task_logic(self) -> None:
        tdos = await self.get_urls_without_probe()
        await self.link_urls_to_task(
            url_ids=[tdo.url_mapping.url_id for tdo in tdos]
        )
        await self.probe_urls(tdos)
        await self.update_database(tdos)

    async def probe_urls(self, tdos: list[URLProbeTDO]) -> None:
        """Probe URLs and add responses to URLProbeTDO

        Modifies:
            URLProbeTDO.response
        """
        url_to_tdo: dict[str, URLProbeTDO] = {
            tdo.url_mapping.full_url.id_form: tdo for tdo in tdos
        }
        responses = await self.url_request_interface.probe_urls(
            urls=[tdo.url_mapping.full_url for tdo in tdos]
        )
        # Re-associate the responses with the URL mappings
        for response in responses:
            tdo = url_to_tdo[response.original_url.id_form]
            tdo.response = response

    async def update_database(self, tdos: list[URLProbeTDO]) -> None:
        none_tdos: list[URLProbeTDO] = [
            tdo for tdo in tdos if tdo.response is None
        ]
        await self.upload_none_errors(none_tdos)

        non_error_tdos = [
            tdo for tdo in tdos if tdo.response is not None
        ]

        non_redirect_tdos = filter_non_redirect_tdos(non_error_tdos)
        web_metadata_objects: list[URLWebMetadataPydantic] = convert_tdo_to_web_metadata_list(non_redirect_tdos)
        await self.adb_client.bulk_upsert(web_metadata_objects)

        redirect_tdos: list[URLProbeTDO] = filter_redirect_tdos(non_error_tdos)

        # Filter redirects into true redirects and functional equivalents
        redirect_subsets: RedirectTDOSubsets = filter_functionally_equivalent_urls(redirect_tdos)

        await self._insert_true_redirects(redirect_subsets.true_redirects)

        await self._update_functional_equivalents(redirect_subsets.functional_equivalents)

    async def upload_none_errors(
        self,
        tdos: list[URLProbeTDO]
    ) -> None:
        error_url_ids: list[int] = [tdo.url_mapping.url_id for tdo in tdos]
        task_errors = [
            URLTaskErrorSmall(
                url_id=url_id,
                error="TDO response is None"
            )
            for url_id in error_url_ids
        ]
        await self.add_task_errors(task_errors)


    async def _insert_true_redirects(self, tdos: list[URLProbeTDO]) -> None:
        await self.adb_client.run_query_builder(
            InsertRedirectsQueryBuilder(tdos=tdos)
        )

    async def _update_functional_equivalents(self, tdos: list[URLProbeTDO]) -> None:
        # For non-true redirects, treat the redirected URL as the true URL and update database
        url_updates = [
            URLFunctionalEquivalentsUpsertModel(
                id=tdo.url_mapping.url_id,
                url=tdo.response.response.destination.url.without_scheme.rstrip('/'),
                trailing_slash=tdo.response.response.destination.url.without_scheme.endswith('/')
            )
            for tdo in tdos
        ]
        await self.adb_client.bulk_update(url_updates)
        # For these URLs, also update web metadata
        func_equiv_web_metadata_objects: list[URLWebMetadataPydantic] = \
            convert_tdos_with_functional_equivalents_to_web_metadata_list(
                tdos
            )
        await self.adb_client.bulk_upsert(func_equiv_web_metadata_objects)

    async def has_urls_without_probe(self) -> bool:
        return await self.adb_client.run_query_builder(
            HasURLsWithoutProbeQueryBuilder()
        )

