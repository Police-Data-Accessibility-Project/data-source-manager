from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.auto_validated.sqlalchemy import FlagURLAutoValidated
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.conftest import db_data_creator
from tests.helpers.counter import next_int
from tests.helpers.data_creator.core import DBDataCreator

DEFAULT_RECORD_TYPE: RecordType = RecordType.INCARCERATION_RECORDS

class TestValidateTaskHelper:

    def __init__(
        self,
        db_data_creator: DBDataCreator,
        url_id: int,
        agency_id: int,
        location_id: int
    ):
        self.db_data_creator = db_data_creator
        self.adb_client: AsyncDatabaseClient = db_data_creator.adb_client
        self.url_id = url_id
        self.agency_id = agency_id
        self.location_id = location_id


    async def check_url_validated(
        self,
        url_type: URLType,
    ) -> None:
        validated_flags: list[FlagURLValidated] = await self.adb_client.get_all(FlagURLValidated)
        assert len(validated_flags) == 1
        validated_flag: FlagURLValidated = validated_flags[0]
        assert validated_flag.url_id == self.url_id
        assert validated_flag.type == url_type

    async def check_auto_validated(
        self,
    ) -> None:
        auto_validated_flags: list[FlagURLAutoValidated] = await self.adb_client.get_all(FlagURLAutoValidated)
        assert len(auto_validated_flags) == 1
        auto_validated_flag: FlagURLAutoValidated = auto_validated_flags[0]
        assert auto_validated_flag.url_id == self.url_id

    async def check_agency_linked(
        self
    ) -> None:
        links: list[LinkURLAgency] = await self.adb_client.get_all(LinkURLAgency)
        assert len(links) == 1
        link: LinkURLAgency = links[0]
        assert link.url_id == self.url_id
        assert link.agency_id == self.agency_id

    async def check_record_type(
        self,
        record_type: RecordType = DEFAULT_RECORD_TYPE
    ):
        record_types: list[URLRecordType] = await self.adb_client.get_all(URLRecordType)
        assert len(record_types) == 1
        rt: URLRecordType = record_types[0]
        assert rt.url_id == self.url_id
        assert rt.record_type == record_type

    async def add_url_type_suggestions(
        self,
        url_type: URLType,
        count: int = 1
    ):
        for _ in range(count):
            await self.db_data_creator.user_relevant_suggestion(
                suggested_status=url_type,
                url_id=self.url_id,
                user_id=next_int()
            )

    async def add_agency_suggestions(
        self,
        count: int = 1,
        agency_id: int | None = None
    ):
        if agency_id is None:
            agency_id = self.agency_id
        for i in range(count):
            await self.db_data_creator.agency_user_suggestions(
                url_id=self.url_id,
                user_id=next_int(),
                agency_annotation_info=URLAgencyAnnotationPostInfo(
                    suggested_agency=agency_id
                )
            )

    async def add_location_suggestions(
        self,
        count: int = 1,
        location_id: int | None = None
    ):
        if location_id is None:
            location_id = self.location_id
        for i in range(count):
            await self.db_data_creator.add_user_location_suggestion(
                url_id=self.url_id,
                user_id=i,
                location_id=location_id,
            )

    async def add_record_type_suggestions(
        self,
        count: int = 1,
        record_type: RecordType = DEFAULT_RECORD_TYPE
    ):
        for i in range(count):
            await self.db_data_creator.user_record_type_suggestion(
                url_id=self.url_id,
                record_type=record_type,
                user_id=next_int()
            )