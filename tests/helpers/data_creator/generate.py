from datetime import datetime

from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus, RecordType
from src.db.models.impl.batch.pydantic.insert import BatchInsertModel
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.pydantic import LinkBatchURLPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.data_source.pydantic import URLDataSourcePydantic
from tests.helpers.counter import next_int


def generate_batch(
    status: BatchStatus,
    strategy: CollectorType = CollectorType.EXAMPLE,
    date_generated: datetime = datetime.now(),
) -> BatchInsertModel:
    return BatchInsertModel(
        strategy=strategy.value,
        status=status,
        parameters={},
        user_id=1,
        date_generated=date_generated,
    )

def generate_batch_url_links(
    url_ids: list[int],
    batch_id: int
) -> list[LinkBatchURLPydantic]:
    return [
        LinkBatchURLPydantic(
            url_id=url_id,
            batch_id=batch_id,
        )
        for url_id in url_ids
    ]

def generate_urls(
    status: URLStatus = URLStatus.OK,
    source: URLSource = URLSource.COLLECTOR,
    collector_metadata: dict | None = None,
    count: int = 1
) -> list[URLInsertModel]:
    results: list[URLInsertModel] = []
    for i in range(count):
        val: int = next_int()
        results.append(URLInsertModel(
            url=f"http://example.com/{val}",
            status=status,
            source=source,
            name=f"Example {val}",
            collector_metadata=collector_metadata,
        ))
    return results

def generate_validated_flags(
    url_ids: list[int],
    validation_type: URLType,
) -> list[FlagURLValidatedPydantic]:
    return [
        FlagURLValidatedPydantic(
            url_id=url_id,
            type=validation_type,
        )
        for url_id in url_ids
    ]

def generate_url_data_sources(
    url_ids: list[int],
) -> list[URLDataSourcePydantic]:
    return [
        URLDataSourcePydantic(
            url_id=url_id,
            data_source_id=url_id,
        )
        for url_id in url_ids
    ]