from datetime import datetime

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus, RecordType
from src.db import County, Locality, USState
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.batch.pydantic.insert import BatchInsertModel
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.link.batch_url.pydantic import LinkBatchURLPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.data_source.pydantic import URLDataSourcePydantic
from tests.helpers.data_creator.generate import generate_batch, generate_urls, generate_validated_flags, \
    generate_url_data_sources, generate_batch_url_links
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


async def create_batch(
    adb_client: AsyncDatabaseClient,
    status: BatchStatus = BatchStatus.READY_TO_LABEL,
    strategy: CollectorType = CollectorType.EXAMPLE,
    date_generated: datetime = datetime.now(),
) -> int:
    batch: BatchInsertModel = generate_batch(status=status, strategy=strategy, date_generated=date_generated)
    return (await adb_client.bulk_insert([batch], return_ids=True))[0]

async def create_urls(
    adb_client: AsyncDatabaseClient,
    status: URLStatus = URLStatus.OK,
    source: URLSource = URLSource.COLLECTOR,
    record_type: RecordType | None = RecordType.RESOURCES,
    collector_metadata: dict | None = None,
    count: int = 1
) -> list[URLMapping]:
    urls: list[URLInsertModel] = generate_urls(
        status=status,
        source=source,
        record_type=record_type,
        collector_metadata=collector_metadata,
        count=count,
    )
    url_ids = await adb_client.bulk_insert(urls, return_ids=True)
    return [URLMapping(url_id=url_id, url=url.url) for url_id, url in zip(url_ids, urls)]

async def create_validated_flags(
    adb_client: AsyncDatabaseClient,
    url_ids: list[int],
    validation_type: URLValidatedType,
) -> None:
    validated_flags: list[FlagURLValidatedPydantic] = generate_validated_flags(
        url_ids=url_ids,
        validation_type=validation_type,
    )
    await adb_client.bulk_insert(validated_flags)

async def create_url_data_sources(
    adb_client: AsyncDatabaseClient,
    url_ids: list[int],
) -> None:
    url_data_sources: list[URLDataSourcePydantic] = generate_url_data_sources(
        url_ids=url_ids,
    )
    await adb_client.bulk_insert(url_data_sources)

async def create_batch_url_links(
    adb_client: AsyncDatabaseClient,
    url_ids: list[int],
    batch_id: int,
) -> None:
    batch_url_links: list[LinkBatchURLPydantic] = generate_batch_url_links(
        url_ids=url_ids,
        batch_id=batch_id,
    )
    await adb_client.bulk_insert(batch_url_links)

async def create_state(
    adb_client: AsyncDatabaseClient,
    name: str,
    iso: str
) -> USStateCreationInfo:

    us_state_insert_model = USState(
        state_name=name,
        state_iso=iso,
    )
    us_state_id: int = await adb_client.add(
        us_state_insert_model,
        return_id=True
    )
    location_id: int = await adb_client.get_location_id(
        us_state_id=us_state_id,
    )
    return USStateCreationInfo(
        us_state_id=us_state_id,
        location_id=location_id,
    )

async def create_county(
    adb_client: AsyncDatabaseClient,
    state_id: int,
    name: str
) -> CountyCreationInfo:
    county_insert_model = County(
        name=name,
        state_id=state_id,
    )
    county_id: int = await adb_client.add(
        county_insert_model,
        return_id=True
    )
    location_id: int = await adb_client.get_location_id(
        us_state_id=state_id,
        county_id=county_id
    )
    return CountyCreationInfo(
        county_id=county_id,
        location_id=location_id,
    )

async def create_locality(
    adb_client: AsyncDatabaseClient,
    state_id: int,
    county_id: int,
    name: str
) -> LocalityCreationInfo:
    locality_insert_model = Locality(
        name=name,
        county_id=county_id,
    )
    locality_id: int = await adb_client.add(
        locality_insert_model,
        return_id=True
    )
    location_id: int = await adb_client.get_location_id(
        us_state_id=state_id,
        county_id=county_id,
        locality_id=locality_id
    )
    return LocalityCreationInfo(
        locality_id=locality_id,
        location_id=location_id,
    )