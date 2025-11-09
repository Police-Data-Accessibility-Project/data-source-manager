from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from pdap_access_manager import ResponseInfo

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.submit_meta_urls.core import SubmitMetaURLsTaskOperator
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.meta_urls.enums import SubmitMetaURLsStatus
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_submit_meta_urls(
    db_data_creator: DBDataCreator,
    mock_pdap_client: PDAPClient,
):
    """
    Test Submit Meta URLs Task Operator
    """


    operator = SubmitMetaURLsTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

    assert not await operator.meets_task_prerequisites()

    # Create validated meta url
    agency_id: int = (await db_data_creator.create_agencies(count=1))[0]

    mapping: SimpleURLMapping = (await db_data_creator.create_validated_urls(
        validation_type=URLType.META_URL
    ))[0]
    await db_data_creator.link_urls_to_agencies(
        url_ids=[mapping.url_id],
        agency_ids=[agency_id]
    )

    mock_pdap_client.access_manager.make_request = AsyncMock(
        return_value=ResponseInfo(
            status_code=HTTPStatus.OK,
            data={
                "meta_urls": [
                    {
                        "url": f"https://{mapping.url}",
                        "agency_id": agency_id,
                        "status": SubmitMetaURLsStatus.SUCCESS.value,
                        "meta_url_id": 2,
                        "error": None,
                    },
                ]
            }
        )
    )


    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    urls: list[URL] = await db_data_creator.adb_client.get_all(URL)
    assert len(urls) == 1
    url: URL = urls[0]
    assert url.status == URLStatus.OK

    url_ds_meta_urls: list[DSAppLinkMetaURL] = await db_data_creator.adb_client.get_all(DSAppLinkMetaURL)
    assert len(url_ds_meta_urls) == 1
    url_ds_meta_url: DSAppLinkMetaURL = url_ds_meta_urls[0]
    assert url_ds_meta_url.url_id == url.id
    assert url_ds_meta_url.ds_meta_url_id == 2
    assert url_ds_meta_url.agency_id == agency_id