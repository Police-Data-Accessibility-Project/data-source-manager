import pytest

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.util.models.full_url import FullURL
from tests.automated.integration.tasks.url.impl.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.impl.probe.constants import TEST_URL
from tests.automated.integration.tasks.url.impl.probe.setup.manager import TestURLProbeSetupManager
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_url_probe_task_functional_equivalent(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL:
    - is functionally equivalent to the original URL
    The existing URL should be updated to the functional equivalent
    And no web metadata added.
    """

    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_redirect_probe_response(
            redirect_status_code=303,
            dest_status_code=303,
            dest_content_type=None,
            dest_error=None,
            redirect_url=FullURL(TEST_URL + "/")
        )
    )
    url_id = await setup_manager.setup_url()
    await run_task_and_confirm_success(operator)

    urls: list[URL] = await setup_manager.adb_client.get_all(URL)
    assert len(urls) == 1
    url: URL = urls[0]

    assert url.url == TEST_URL
    assert url.trailing_slash is True

    # Web metadata should be added
    web_metadata: list[URLWebMetadata] = await setup_manager.adb_client.get_all(URLWebMetadata)
    assert len(web_metadata) == 1
