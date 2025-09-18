from datetime import datetime
from http import HTTPStatus
from typing import Optional, Any

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.duplicate.pydantic.insert import DuplicateInsertInfo
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.client.sync import DatabaseClient
from src.db.enums import TaskType
from src.collectors.enums import CollectorType, URLStatus
from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.enums import BatchStatus, SuggestionType, RecordType, SuggestedStatus
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.counter import next_int
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.agency import AgencyCommand
from tests.helpers.data_creator.commands.impl.batch import DBDataCreatorBatchCommand
from tests.helpers.data_creator.commands.impl.batch_v2 import BatchV2Command
from tests.helpers.data_creator.commands.impl.html_data import HTMLDataCreatorCommand
from tests.helpers.data_creator.commands.impl.suggestion.agency_confirmed import AgencyConfirmedSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.auto.agency_.core import AgencyAutoSuggestionsCommand
from tests.helpers.data_creator.commands.impl.suggestion.auto.record_type import AutoRecordTypeSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.auto.relevant import AutoRelevantSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.agency import AgencyUserSuggestionsCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.record_type import UserRecordTypeSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.relevant import UserRelevantSuggestionCommand
from tests.helpers.data_creator.commands.impl.url_metadata import URLMetadataCommand
from tests.helpers.data_creator.commands.impl.urls_.query import URLsDBDataCreatorCommand
from tests.helpers.data_creator.commands.impl.urls_v2.core import URLsV2Command
from tests.helpers.data_creator.commands.impl.urls_v2.response import URLsV2Response
from tests.helpers.data_creator.create import create_urls, create_batch, create_batch_url_links, create_validated_flags, \
    create_url_data_sources, create_state, create_county, create_locality
from tests.helpers.data_creator.models.clients import DBDataCreatorClientContainer
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.simple_test_data_functions import generate_test_name


class DBDataCreator:
    """
    Assists in the creation of test data
    """
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        if db_client is not None:
            self.db_client = db_client
        else:
            self.db_client = DatabaseClient()
        self.adb_client: AsyncDatabaseClient = AsyncDatabaseClient()
        self.clients = DBDataCreatorClientContainer(
            adb=self.adb_client,
            db=self.db_client
        )

    def run_command_sync(self, command: DBDataCreatorCommandBase) -> Any:
        command.load_clients(self.clients)
        return command.run_sync()

    async def run_command(self, command: DBDataCreatorCommandBase) -> Any:
        command.load_clients(self.clients)
        return await command.run()

    def batch(
        self,
        strategy: CollectorType = CollectorType.EXAMPLE,
        batch_status: BatchStatus = BatchStatus.IN_PROCESS,
        created_at: Optional[datetime] = None
    ) -> int:
        command = DBDataCreatorBatchCommand(
            strategy=strategy,
            batch_status=batch_status,
            created_at=created_at
        )
        return self.run_command_sync(command)

    async def task(self, url_ids: Optional[list[int]] = None) -> int:
        task_id = await self.adb_client.initiate_task(task_type=TaskType.HTML)
        if url_ids is not None:
            await self.adb_client.link_urls_to_task(task_id=task_id, url_ids=url_ids)
        return task_id

    async def batch_v2(
        self,
        parameters: TestBatchCreationParameters
    ) -> BatchURLCreationInfoV2:
        return await self.run_command(BatchV2Command(parameters))

    async def url_v2(
        self,
        parameters: list[TestURLCreationParameters],
        batch_id: int | None = None,
        created_at: datetime | None = None
    ) -> URLsV2Response:
        return await self.run_command(
            URLsV2Command(
                parameters=parameters,
                batch_id=batch_id,
                created_at=created_at
            )
        )


    async def batch_and_urls(
            self,
            strategy: CollectorType = CollectorType.EXAMPLE,
            url_count: int = 3,
            with_html_content: bool = False,
            batch_status: BatchStatus = BatchStatus.READY_TO_LABEL,
            url_status: URLCreationEnum = URLCreationEnum.OK
    ) -> BatchURLCreationInfo:
        batch_id = self.batch(
            strategy=strategy,
            batch_status=batch_status
        )
        if batch_status in (BatchStatus.ERROR, BatchStatus.ABORTED):
            return BatchURLCreationInfo(
                batch_id=batch_id,
                url_ids=[],
                urls=[]
            )
        iuis: InsertURLsInfo = self.urls(
            batch_id=batch_id,
            url_count=url_count,
            outcome=url_status
        )
        url_ids = [iui.url_id for iui in iuis.url_mappings]
        if with_html_content:
            await self.html_data(url_ids)

        return BatchURLCreationInfo(
            batch_id=batch_id,
            url_ids=url_ids,
            urls=[iui.url for iui in iuis.url_mappings]
        )

    async def agency(self) -> int:
        return await self.run_command(AgencyCommand())

    async def auto_relevant_suggestions(self, url_id: int, relevant: bool = True):
        await self.run_command(
            AutoRelevantSuggestionCommand(
                url_id=url_id,
                relevant=relevant
            )
        )

    async def user_relevant_suggestion(
            self,
            url_id: int,
            user_id: int | None = None,
            suggested_status: SuggestedStatus = SuggestedStatus.RELEVANT
    ) -> None:
        await self.run_command(
            UserRelevantSuggestionCommand(
                url_id=url_id,
                user_id=user_id,
                suggested_status=suggested_status
            )
        )

    async def user_record_type_suggestion(
            self,
            url_id: int,
            record_type: RecordType,
            user_id: Optional[int] = None,
    ) -> None:
        await self.run_command(
            UserRecordTypeSuggestionCommand(
                url_id=url_id,
                record_type=record_type,
                user_id=user_id
            )
        )

    async def auto_record_type_suggestions(
        self,
        url_id: int,
        record_type: RecordType
    ):
        await self.run_command(
            AutoRecordTypeSuggestionCommand(
                url_id=url_id,
                record_type=record_type
            )
        )

    async def auto_suggestions(
            self,
            url_ids: list[int],
            num_suggestions: int,
            suggestion_type: SuggestionType.AUTO_SUGGESTION or SuggestionType.UNKNOWN
    ):
        allowed_suggestion_types = [SuggestionType.AUTO_SUGGESTION, SuggestionType.UNKNOWN]
        if suggestion_type not in allowed_suggestion_types:
            raise ValueError(f"suggestion_type must be one of {allowed_suggestion_types}")
        if suggestion_type == SuggestionType.UNKNOWN and num_suggestions > 1:
            raise ValueError("num_suggestions must be 1 when suggestion_type is unknown")
        
        for url_id in url_ids:
            await self.run_command(
                AgencyAutoSuggestionsCommand(
                    url_id=url_id,
                    count=num_suggestions,
                    suggestion_type=suggestion_type
                )
            )

    async def confirmed_suggestions(self, url_ids: list[int]):
        for url_id in url_ids:
            await self.adb_client.add_confirmed_agency_url_links(
                suggestions=[
                    URLAgencySuggestionInfo(
                        url_id=url_id,
                        suggestion_type=SuggestionType.CONFIRMED,
                        pdap_agency_id=await self.agency()
                    )
                ]
            )

    async def manual_suggestion(self, user_id: int, url_id: int, is_new: bool = False):
        await self.adb_client.add_agency_manual_suggestion(
            agency_id=await self.agency(),
            url_id=url_id,
            user_id=user_id,
            is_new=is_new
        )


    def urls(
            self,
            batch_id: int,
            url_count: int,
            collector_metadata: dict | None = None,
            outcome: URLCreationEnum = URLCreationEnum.OK,
            created_at: datetime | None = None
    ) -> InsertURLsInfo:
        command = URLsDBDataCreatorCommand(
            batch_id=batch_id,
            url_count=url_count,
            collector_metadata=collector_metadata,
            status=outcome,
            created_at=created_at
        )
        return self.run_command_sync(command)

    async def url_miscellaneous_metadata(
            self,
            url_id: int,
            name: str = "Test Name",
            description: str = "Test Description",
            record_formats: Optional[list[str]] = None,
            data_portal_type: Optional[str] = "Test Data Portal Type",
            supplying_entity: Optional[str] = "Test Supplying Entity"
    ) -> None:
        if record_formats is None:
            record_formats = ["Test Record Format", "Test Record Format 2"]

        tdo = URLMiscellaneousMetadataTDO(
            url_id=url_id,
            collector_metadata={},
            collector_type=CollectorType.EXAMPLE,
            record_formats=record_formats,
            name=name,
            description=description,
            data_portal_type=data_portal_type,
            supplying_entity=supplying_entity
        )

        await self.adb_client.add_miscellaneous_metadata([tdo])


    def duplicate_urls(
        self,
        duplicate_batch_id: int,
        url_ids: list[int]
    ) -> None:
        """
        Create duplicates for all given url ids, and associate them
        with the given batch
        """
        duplicate_infos = []
        for url_id in url_ids:
            dup_info = DuplicateInsertInfo(
                batch_id=duplicate_batch_id,
                original_url_id=url_id
            )
            duplicate_infos.append(dup_info)

        self.db_client.insert_duplicates(duplicate_infos)

    async def html_data(self, url_ids: list[int]) -> None:
        command = HTMLDataCreatorCommand(
            url_ids=url_ids
        )
        await self.run_command(command)

    async def error_info(
            self,
            url_ids: list[int],
            task_id: Optional[int] = None
    ) -> None:
        if task_id is None:
            task_id = await self.task()
        error_infos = []
        for url_id in url_ids:
            url_error_info = URLErrorInfoPydantic(
                url_id=url_id,
                error="test error",
                task_id=task_id
            )
            error_infos.append(url_error_info)
        await self.adb_client.add_url_error_infos(error_infos)


    async def agency_auto_suggestions(
            self,
            url_id: int,
            count: int,
            suggestion_type: SuggestionType = SuggestionType.AUTO_SUGGESTION
    ) -> None:
        await self.run_command(
            AgencyAutoSuggestionsCommand(
                url_id=url_id,
                count=count,
                suggestion_type=suggestion_type
            )
        )

    async def agency_confirmed_suggestion(
            self,
            url_id: int
    ) -> int:
        """
        Create a confirmed agency suggestion and return the auto-generated pdap_agency_id.
        """
        return await self.run_command(
            AgencyConfirmedSuggestionCommand(url_id)
        )

    async def agency_user_suggestions(
            self,
            url_id: int,
            user_id: int | None = None,
            agency_annotation_info: URLAgencyAnnotationPostInfo | None = None
    ) -> None:
        await self.run_command(
            AgencyUserSuggestionsCommand(
                url_id=url_id,
                user_id=user_id,
                agency_annotation_info=agency_annotation_info
            )
        )

    async def url_metadata(
            self,
            url_ids: list[int],
            content_type: str = "text/html",
            status_code: int = HTTPStatus.OK.value
    ) -> None:
        await self.run_command(
            URLMetadataCommand(
                url_ids=url_ids,
                content_type=content_type,
                status_code=status_code
            )
        )

    async def create_validated_urls(
        self,
        record_type: RecordType = RecordType.RESOURCES,
        validation_type: URLValidatedType = URLValidatedType.DATA_SOURCE,
        count: int = 1
    ) -> list[URLMapping]:
        url_mappings: list[URLMapping] = await self.create_urls(
            record_type=record_type,
            count=count
        )
        url_ids: list[int] = [url_mapping.url_id for url_mapping in url_mappings]
        await self.create_validated_flags(
            url_ids=url_ids,
            validation_type=validation_type
        )
        return url_mappings

    async def create_submitted_urls(
        self,
        record_type: RecordType = RecordType.RESOURCES,
        count: int = 1
    ) -> list[URLMapping]:
        url_mappings: list[URLMapping] = await self.create_urls(
            record_type=record_type,
            count=count
        )
        url_ids: list[int] = [url_mapping.url_id for url_mapping in url_mappings]
        await self.create_validated_flags(
            url_ids=url_ids,
            validation_type=URLValidatedType.DATA_SOURCE
        )
        await self.create_url_data_sources(url_ids=url_ids)
        return url_mappings


    async def create_urls(
        self,
        status: URLStatus = URLStatus.OK,
        source: URLSource = URLSource.COLLECTOR,
        record_type: RecordType | None = RecordType.RESOURCES,
        collector_metadata: dict | None = None,
        count: int = 1,
        batch_id: int | None = None
    ) -> list[URLMapping]:

        url_mappings: list[URLMapping] = await create_urls(
            adb_client=self.adb_client,
            status=status,
            source=source,
            record_type=record_type,
            collector_metadata=collector_metadata,
            count=count
        )
        url_ids: list[int] = [url_mapping.url_id for url_mapping in url_mappings]
        if batch_id is not None:
            await self.create_batch_url_links(
                url_ids=url_ids,
                batch_id=batch_id
            )
        return url_mappings

    async def create_batch(
        self,
        status: BatchStatus = BatchStatus.READY_TO_LABEL,
        strategy: CollectorType = CollectorType.EXAMPLE,
        date_generated: datetime = datetime.now(),
    ) -> int:
        return await create_batch(
            adb_client=self.adb_client,
            status=status,
            strategy=strategy,
            date_generated=date_generated
        )

    async def create_batch_url_links(
        self,
        url_ids: list[int],
        batch_id: int,
    ) -> None:
        await create_batch_url_links(
            adb_client=self.adb_client,
            url_ids=url_ids,
            batch_id=batch_id
        )

    async def create_validated_flags(
        self,
        url_ids: list[int],
        validation_type: URLValidatedType,
    ) -> None:
        await create_validated_flags(
            adb_client=self.adb_client,
            url_ids=url_ids,
            validation_type=validation_type
        )

    async def create_url_data_sources(
        self,
        url_ids: list[int],
    ) -> None:
        await create_url_data_sources(
            adb_client=self.adb_client,
            url_ids=url_ids
        )

    async def create_url_agency_links(
        self,
        url_ids: list[int],
        agency_ids: list[int],
    ) -> None:
        links: list[LinkURLAgency] = []
        for url_id in url_ids:
            for agency_id in agency_ids:
                link = LinkURLAgency(
                    url_id=url_id,
                    agency_id=agency_id,
                )
                links.append(link)
        await self.adb_client.add_all(links)

    async def create_agency(self, agency_id: int = 1) -> None:
        agency = Agency(
            agency_id=agency_id,
            name=generate_test_name(agency_id),
            state=None,
            county=None,
            locality=None
        )
        await self.adb_client.add_all([agency])

    async def create_agencies(self, count: int = 3) -> list[int]:
        agencies: list[Agency] = []
        agency_ids: list[int] = []
        for _ in range(count):
            agency_id = next_int()
            agency = Agency(
                agency_id=agency_id,
                name=generate_test_name(agency_id),
                state=None,
                county=None,
                locality=None
            )
            agencies.append(agency)
            agency_ids.append(agency_id)
        await self.adb_client.add_all(agencies)
        return agency_ids

    async def flag_as_root(self, url_ids: list[int]) -> None:
        flag_root_urls: list[FlagRootURL] = [
            FlagRootURL(url_id=url_id) for url_id in url_ids
        ]
        await self.adb_client.add_all(flag_root_urls)

    async def link_urls_to_root(self, url_ids: list[int], root_url_id: int) -> None:
        links: list[LinkURLRootURL] = [
            LinkURLRootURL(url_id=url_id, root_url_id=root_url_id) for url_id in url_ids
        ]
        await self.adb_client.add_all(links)

    async def link_urls_to_agencies(self, url_ids: list[int], agency_ids: list[int]) -> None:
        assert len(url_ids) == len(agency_ids)
        links: list[LinkURLAgency] = []
        for url_id, agency_id in zip(url_ids, agency_ids):
            link = LinkURLAgency(
                url_id=url_id,
                agency_id=agency_id
            )
            links.append(link)
        await self.adb_client.add_all(links)

    async def create_web_metadata(
        self,
        url_ids: list[int],
        status_code: int = 200,
    ):
        web_metadata: list[URLWebMetadata] = [
            URLWebMetadata(
                url_id=url_id,
                status_code=status_code,
                accessed=True,
                content_type="text/html",
            )
            for url_id in url_ids
        ]
        await self.adb_client.add_all(web_metadata)

    async def create_us_state(
        self,
        name: str,
        iso:str
    ) -> USStateCreationInfo:
        return await create_state(
            adb_client=self.adb_client,
            name=name,
            iso=iso,
        )

    async def create_county(
        self,
        state_id: int,
        name: str,
    ) -> CountyCreationInfo:
        return await create_county(
            adb_client=self.adb_client,
            state_id=state_id,
            name=name,
        )

    async def create_locality(
        self,
        state_id: int,
        county_id: int,
        name: str,
    ) -> LocalityCreationInfo:
        return await create_locality(
            adb_client=self.adb_client,
            state_id=state_id,
            county_id=county_id,
            name=name,
        )

    async def add_compressed_html(
        self,
        url_ids: list[int],
    ):
        compressed_html_inserts: list[URLCompressedHTML] = [
            URLCompressedHTML(
                url_id=url_id,
                compressed_html=b"<html>Test HTML</html>"
            )
            for url_id in url_ids
        ]
        await self.adb_client.add_all(compressed_html_inserts)