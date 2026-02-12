from typing import AsyncGenerator
from urllib.parse import urlparse

import aiohttp

from src.collectors.impl.internet_archive.dtos.output import (
    InternetArchiveOutputDTO,
    InternetArchiveURLResult,
)
from src.collectors.impl.internet_archive.filter import InternetArchiveCDXFilter
from src.external.internet_archives.client import InternetArchivesClient


class InternetArchiveCrawler:

    def __init__(
        self,
        urls: list[str],
        max_results_per_domain: int = 10000,
        exclude_patterns: list[str] | None = None,
        mime_type_allowlist: list[str] | None = None,
    ):
        self.urls = urls
        self.max_results_per_domain = max_results_per_domain
        self.exclude_patterns = exclude_patterns or []
        self.mime_type_allowlist = mime_type_allowlist or ["text/html"]
        self.results: list[InternetArchiveOutputDTO] = []

    def _extract_domains(self) -> list[str]:
        domains = set()
        for url in self.urls:
            parsed = urlparse(url)
            if parsed.hostname:
                domains.add(parsed.hostname.lower())
        return sorted(domains)

    async def run(self) -> AsyncGenerator[str, None]:
        seed_urls_lower = {u.lower().rstrip("/") for u in self.urls}
        domains = self._extract_domains()

        async with aiohttp.ClientSession() as session:
            client = InternetArchivesClient(session=session)

            for domain in domains:
                yield f"Searching {domain}..."

                result = await client.search_domain_urls(
                    domain=domain, limit=self.max_results_per_domain
                )

                if result.error:
                    yield f"Error searching {domain}: {result.error}"
                    continue

                total_captures = len(result.captures)

                filtered = InternetArchiveCDXFilter.filter_all(
                    captures=result.captures,
                    allowlist=self.mime_type_allowlist,
                    exclude_patterns=self.exclude_patterns,
                )

                # Remove seed URLs from results
                filtered = [
                    c for c in filtered
                    if c.original.lower().rstrip("/") not in seed_urls_lower
                ]

                url_results = [
                    InternetArchiveURLResult(
                        url=c.original,
                        archive_url=(
                            f"https://web.archive.org/web/"
                            f"{c.timestamp}/{c.original}"
                        ),
                        timestamp=c.timestamp,
                        digest=c.digest,
                    )
                    for c in filtered
                ]

                self.results.append(
                    InternetArchiveOutputDTO(
                        domain=domain, urls=url_results
                    )
                )

                yield (
                    f"Searching {domain}... Found {total_captures} captures, "
                    f"{len(url_results)} after filtering"
                )

        total = sum(len(r.urls) for r in self.results)
        yield f"Found {total} total URLs across {len(domains)} domain(s)"
