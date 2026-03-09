"""Unit tests for Internet Archive save lifecycle."""
from unittest import mock

import pytest
from aiohttp import ClientSession

from src.external.internet_archives.client import InternetArchivesClient

TEST_URL = "https://example.gov/path"


@pytest.fixture
def mock_env() -> mock.MagicMock:
    """Patch environment access for S3 key loading."""
    mock_path = "src.external.internet_archives.client.Env"
    with mock.patch(mock_path) as mock_env_cls:
        mock_env_instance = mock.MagicMock()
        mock_env_instance.str.return_value = "fake_s3_keys"
        mock_env_cls.return_value = mock_env_instance
        yield mock_env_cls


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_save_success_when_status_completes() -> None:
    session = mock.MagicMock(spec=ClientSession)
    client = InternetArchivesClient(session)

    with (
        mock.patch.object(client, "_save_url", new=mock.AsyncMock(return_value="job_1")) as mock_save_url,
        mock.patch.object(
            client,
            "_wait_for_save_completion",
            new=mock.AsyncMock(return_value=None)
        ) as mock_wait
    ):
        response = await client.save_to_internet_archives(TEST_URL)

    mock_save_url.assert_awaited_once_with(TEST_URL)
    mock_wait.assert_awaited_once_with("job_1")
    assert response.url == TEST_URL
    assert response.error is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_save_error_when_status_fails() -> None:
    session = mock.MagicMock(spec=ClientSession)
    client = InternetArchivesClient(session)

    with (
        mock.patch.object(client, "_save_url", new=mock.AsyncMock(return_value="job_1")),
        mock.patch.object(
            client,
            "_wait_for_save_completion",
            new=mock.AsyncMock(return_value="Failed to capture URL")
        )
    ):
        response = await client.save_to_internet_archives(TEST_URL)

    assert response.url == TEST_URL
    assert response.error == "Failed to capture URL"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_save_error_when_submit_raises() -> None:
    session = mock.MagicMock(spec=ClientSession)
    client = InternetArchivesClient(session)

    with mock.patch.object(
        client, "_save_url", new=mock.AsyncMock(side_effect=RuntimeError("boom"))
    ):
        response = await client.save_to_internet_archives(TEST_URL)

    assert response.url == TEST_URL
    assert response.error == "RuntimeError: boom"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_wait_for_save_completion_retries_until_success() -> None:
    session = mock.MagicMock(spec=ClientSession)
    client = InternetArchivesClient(session)

    mock_status = mock.AsyncMock(
        side_effect=[
            {"status": "pending"},
            {"status": "success"},
        ]
    )

    with mock.patch.object(client, "_get_save_status", new=mock_status):
        error = await client._wait_for_save_completion(
            "job_1",
            max_attempts=2,
            poll_interval_seconds=0
        )

    assert error is None
    assert mock_status.await_count == 2


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_wait_for_save_completion_returns_failure_message() -> None:
    session = mock.MagicMock(spec=ClientSession)
    client = InternetArchivesClient(session)

    mock_status = mock.AsyncMock(
        return_value={
            "status": "failed",
            "message": "robots.txt blocked capture"
        }
    )

    with mock.patch.object(client, "_get_save_status", new=mock_status):
        error = await client._wait_for_save_completion(
            "job_1",
            max_attempts=1,
            poll_interval_seconds=0
        )

    assert error == "robots.txt blocked capture"
