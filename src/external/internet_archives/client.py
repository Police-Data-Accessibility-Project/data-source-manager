"""Client for the Internet Archive CDX and Save APIs."""
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

    async def _save_url(self: "InternetArchivesClient", url: str) -> int:
        async with self.session.post(
            "http://web.archive.org/save",
            data={
                "url": url,
                "skip_first_archive": 1
            },
            headers={
                "Authorization": f"LOW {self.s3_keys}",
                "Accept": "application/json"
            }
        ) as response:
            response.raise_for_status()
            return response.status

    async def save_to_internet_archives(self: "InternetArchivesClient", url: str) -> InternetArchivesSaveResponseInfo:
        """Save a URL to the Internet Archive."""
        try:
            _: int = await self._save_url(url)
        except Exception as e:
            return InternetArchivesSaveResponseInfo(
                url=url,
                error=f"{e.__class__.__name__}: {e}"
            )

        return InternetArchivesSaveResponseInfo(
            url=url,
            error=None
        )
