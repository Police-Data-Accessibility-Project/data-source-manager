from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.impl.internet_archives.save.filter import filter_save_responses
from src.core.tasks.scheduled.impl.internet_archives.save.mapper import URLToEntryMapper
from src.core.tasks.scheduled.impl.internet_archives.save.models.entry import InternetArchivesSaveTaskEntry
from src.core.tasks.scheduled.impl.internet_archives.save.models.mapping import URLInternetArchivesSaveResponseMapping
from src.core.tasks.scheduled.impl.internet_archives.save.models.subset import IASaveURLMappingSubsets
from src.core.tasks.scheduled.impl.internet_archives.save.queries.get import \
    GetURLsForInternetArchivesSaveTaskQueryBuilder
from src.core.tasks.scheduled.impl.internet_archives.save.queries.prereq import \
    MeetsPrerequisitesForInternetArchivesSaveQueryBuilder
from src.core.tasks.scheduled.impl.internet_archives.save.queries.update import \
    UpdateInternetArchivesSaveMetadataQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.impl.url.internet_archives.save.pydantic import URLInternetArchiveSaveMetadataPydantic
from src.external.internet_archives.client import InternetArchivesClient
from src.external.internet_archives.models.save_response import InternetArchivesSaveResponseInfo


class InternetArchivesSaveTaskOperator(
    ScheduledTaskOperatorBase,
    HasPrerequisitesMixin,
    LinkURLsMixin
):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        ia_client: InternetArchivesClient
    ):
        super().__init__(adb_client)
        self.ia_client = ia_client

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            MeetsPrerequisitesForInternetArchivesSaveQueryBuilder()
        )

    @property
    def task_type(self) -> TaskType:
        return TaskType.IA_SAVE

    async def inner_task_logic(self) -> None:
        entries: list[InternetArchivesSaveTaskEntry] = await self._get_valid_urls()
        mapper = URLToEntryMapper(entries)
        url_ids = [entry.url_id for entry in entries]
        await self.link_urls_to_task(url_ids=url_ids)

        # Save all to internet archives and get responses
        resp_mappings: list[URLInternetArchivesSaveResponseMapping] = await self._save_all_to_internet_archives(
            mapper.get_all_urls()
        )

        # Separate errors from successful saves
        subsets: IASaveURLMappingSubsets = filter_save_responses(resp_mappings)

        # Save errors
        await self._add_errors_to_db(mapper, responses=subsets.error)

        # Save successful saves that are new archive entries
        await self._save_new_saves_to_db(mapper, ia_mappings=subsets.success)

        # Save successful saves that are existing archive entries
        await self._save_existing_saves_to_db(mapper, ia_mappings=subsets.success)



    async def _save_all_to_internet_archives(self, urls: list[str]) -> list[URLInternetArchivesSaveResponseMapping]:
        resp_mappings: list[URLInternetArchivesSaveResponseMapping] = []
        for url in urls:
            resp: InternetArchivesSaveResponseInfo = await self.ia_client.save_to_internet_archives(url)
            mapping = URLInternetArchivesSaveResponseMapping(
                url=url,
                response=resp
            )
            resp_mappings.append(mapping)
        return resp_mappings

    async def _get_valid_urls(self) -> list[InternetArchivesSaveTaskEntry]:
        return await self.adb_client.run_query_builder(
            GetURLsForInternetArchivesSaveTaskQueryBuilder()
        )

    async def _add_errors_to_db(
        self,
        mapper: URLToEntryMapper,
        responses: list[InternetArchivesSaveResponseInfo]
    ) -> None:
        error_info_list: list[URLErrorPydanticInfo] = []
        for response in responses:
            url_id = mapper.get_url_id(response.url)
            url_error_info = URLErrorPydanticInfo(
                url_id=url_id,
                error=response.error,
                task_id=self.task_id
            )
            error_info_list.append(url_error_info)
        await self.adb_client.bulk_insert(error_info_list)

    async def _save_new_saves_to_db(
        self,
        mapper: URLToEntryMapper,
        ia_mappings: list[URLInternetArchivesSaveResponseMapping]
    ) -> None:
        insert_objects: list[URLInternetArchiveSaveMetadataPydantic] = []
        for ia_mapping in ia_mappings:
            is_new = mapper.get_is_new(ia_mapping.url)
            if not is_new:
                continue
            insert_object = URLInternetArchiveSaveMetadataPydantic(
                url_id=mapper.get_url_id(ia_mapping.url),
            )
            insert_objects.append(insert_object)
        await self.adb_client.bulk_insert(insert_objects)

    async def _save_existing_saves_to_db(
        self,
        mapper: URLToEntryMapper,
        ia_mappings: list[URLInternetArchivesSaveResponseMapping]
    ) -> None:
        url_ids: list[int] = []
        for ia_mapping in ia_mappings:
            is_new = mapper.get_is_new(ia_mapping.url)
            if is_new:
                continue
            url_ids.append(mapper.get_url_id(ia_mapping.url))
        await self.adb_client.run_query_builder(
            UpdateInternetArchivesSaveMetadataQueryBuilder(
                url_ids=url_ids
            )
        )