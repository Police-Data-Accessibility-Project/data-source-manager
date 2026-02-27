"""Client for the Internet Archive CDX and Save APIs."""
from asyncio import sleep
from asyncio import Semaphore

from aiolimiter import AsyncLimiter
from aiohttp import ClientSession

from src.external.internet_archives.convert import convert_capture_to_archive_metadata
from src.external.internet_archives.models.capture import IACapture
from src.external.internet_archives.models.domain_search import IADomainSearchResult
from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping
from src.external.internet_archives.models.save_response import InternetArchivesSaveResponseInfo

from environs import Env

limiter = AsyncLimiter(
    max_rate=50,
    time_period=50
)
sem = Semaphore(10)


class InternetArchivesClient:
    """Client for interacting with the Internet Archive APIs."""

    def __init__(
        self: "InternetArchivesClient",
        session: ClientSession
    ) -> None:
        """Initialize with an aiohttp session and load S3 keys from env."""
        self.session = session

        env = Env()
        env.read_env()

        self.s3_keys = env.str("INTERNET_ARCHIVE_S3_KEYS")

    async def search_domain_urls(
        self: "InternetArchivesClient", domain: str, limit: int = 10000
    ) -> IADomainSearchResult:
        """Search for all archived URLs under a domain via the CDX API."""
        params = {
            "url": f"*.{domain}/*",
            "output": "json",
            "filter": "statuscode:200",
            "collapse": "urlkey",
            "fl": "timestamp,original,length,digest,mimetype",
            "limit": str(limit),
            "gzip": "false",
        }
        try:
            async with sem:
                async with limiter:
                    async with self.session.get(
                        "http://web.archive.org/cdx/search/cdx",
                        params=params,
                    ) as response:
                        raw_data = await response.json()
                        if len(raw_data) <= 1:
                            return IADomainSearchResult(
                                domain=domain, captures=[]
                            )
                        fields = raw_data[0]
                        captures = [
                            IACapture(**dict(zip(fields, row)))
                            for row in raw_data[1:]
                        ]
                        return IADomainSearchResult(
                            domain=domain, captures=captures
                        )
        except Exception as e:
            return IADomainSearchResult(
                domain=domain,
                captures=[],
                error=f"{e.__class__.__name__}: {e}",
            )

    async def _get_url_snapshot(self: "InternetArchivesClient", url: str) -> IACapture | None:
        params = {
            "url": url,
            "output": "json",
            "limit": "1",
            "gzip": "false",
            "filter": "statuscode:200",
            "fl": "timestamp,original,length,digest"
        }
        async with sem:
            async with limiter:
                async with self.session.get(
                    "http://web.archive.org/cdx/search/cdx",
                    params=params
                ) as response:
                    raw_data = await response.json()
                    if len(raw_data) == 0:
                        return None
                    fields = raw_data[0]
                    values = raw_data[1]
                    d = dict(zip(fields, values))

                    return IACapture(**d)

    async def search_for_url_snapshot(self: "InternetArchivesClient", url: str) -> InternetArchivesURLMapping:
        """Search for a single URL snapshot in the Internet Archive."""
        try:
            capture: IACapture | None = await self._get_url_snapshot(url)
        except Exception as e:
            return InternetArchivesURLMapping(
                url=url,
                ia_metadata=None,
                error=f"{e.__class__.__name__}: {e}"
            )

        if capture is None:
            return InternetArchivesURLMapping(
                url=url,
                ia_metadata=None,
                error=None
            )

        metadata = convert_capture_to_archive_metadata(capture)
        return InternetArchivesURLMapping(
            url=url,
            ia_metadata=metadata,
            error=None
        )

    async def _save_url(self: "InternetArchivesClient", url: str) -> str:
        async with self.session.post(
            "https://web.archive.org/save",
            data={
                "url": url,
                "skip_first_archive": 1
            },
            headers={
                "Authorization": f"LOW {self.s3_keys}",
                "Accept": "application/json",
                "Capture-Output": "json",
            }
        ) as response:
            response.raise_for_status()
            payload: dict = await response.json(content_type=None)
            job_id = payload.get("job_id")
            if not job_id:
                raise ValueError(
                    f"Save request for URL {url} succeeded without job_id: {payload}"
                )
            return str(job_id)

    async def _get_save_status(self: "InternetArchivesClient", job_id: str) -> dict:
        async with self.session.get(
            f"https://web.archive.org/save/status/{job_id}",
            headers={
                "Authorization": f"LOW {self.s3_keys}",
                "Accept": "application/json"
            }
        ) as response:
            response.raise_for_status()
            return await response.json(content_type=None)

    async def _wait_for_save_completion(
        self: "InternetArchivesClient",
        job_id: str,
        max_attempts: int = 10,
        poll_interval_seconds: float = 2.0
    ) -> str | None:
        for _ in range(max_attempts):
            payload = await self._get_save_status(job_id)
            raw_status = payload.get("status")
            status = str(raw_status).lower() if raw_status is not None else ""

            if status == "success":
                return None

            if status in {"error", "failed", "failure"}:
                status_message = payload.get("message")
                if status_message:
                    return str(status_message)
                return f"Save request failed with payload: {payload}"

            await sleep(poll_interval_seconds)

        return f"Timed out waiting for Internet Archive save completion for job_id={job_id}"

    async def save_to_internet_archives(self: "InternetArchivesClient", url: str) -> InternetArchivesSaveResponseInfo:
        """Save a URL to the Internet Archive."""
        try:
            job_id: str = await self._save_url(url)
            save_error: str | None = await self._wait_for_save_completion(job_id)
            if save_error:
                return InternetArchivesSaveResponseInfo(
                    url=url,
                    error=save_error
                )
        except Exception as e:
            return InternetArchivesSaveResponseInfo(
                url=url,
                error=f"{e.__class__.__name__}: {e}"
            )

        return InternetArchivesSaveResponseInfo(
            url=url,
            error=None
        )
