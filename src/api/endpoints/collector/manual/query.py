from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase
from src.util.models.url_and_scheme import URLAndScheme
from src.util.url import get_url_and_scheme


class UploadManualBatchQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        dto: ManualBatchInputDTO
    ):
        super().__init__()
        self.dto = dto
        self.user_id = user_id


    async def run(self, session: AsyncSession) -> ManualBatchResponseDTO:
        batch = Batch(
            strategy=CollectorType.MANUAL.value,
            status=BatchStatus.READY_TO_LABEL.value,
            parameters={
                "name": self.dto.name
            },
            user_id=self.user_id
        )
        session.add(batch)
        await session.flush()

        batch_id: int = batch.id
        url_ids: list[int] = []
        duplicate_urls: list[str] = []

        for entry in self.dto.entries:
            url_and_scheme: URLAndScheme = get_url_and_scheme(entry.url)

            url = URL(
                url=url_and_scheme.url.rstrip('/'),
                scheme=url_and_scheme.scheme,
                name=entry.name,
                description=entry.description,
                collector_metadata=entry.collector_metadata,
                source=URLSource.MANUAL,
                trailing_slash=url_and_scheme.url.endswith('/'),
            )


            async with session.begin_nested():
                try:
                    session.add(url)
                    await session.flush()
                except IntegrityError:
                    duplicate_urls.append(entry.url)
                    continue
            await session.flush()

            if entry.record_type is not None:
                record_type = URLRecordType(
                    url_id=url.id,
                    record_type=entry.record_type,
                )
                session.add(record_type)


            link = LinkBatchURL(
                batch_id=batch_id,
                url_id=url.id
            )
            session.add(link)

            optional_metadata = URLOptionalDataSourceMetadata(
                url_id=url.id,
                record_formats=entry.record_formats or [],
                data_portal_type=entry.data_portal_type,
                supplying_entity=entry.supplying_entity,
                access_types=[]
            )
            session.add(optional_metadata)
            url_ids.append(url.id)

        return ManualBatchResponseDTO(
            batch_id=batch_id,
            urls=url_ids,
            duplicate_urls=duplicate_urls
        )