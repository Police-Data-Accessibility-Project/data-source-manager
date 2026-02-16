from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.enums import CollectorType
from src.collectors.impl.internet_archive.crawler import InternetArchiveCrawler
from src.collectors.impl.internet_archive.dtos.input import InternetArchiveInputDTO
from src.core.preprocessors.internet_archive import InternetArchivePreprocessor


class InternetArchiveCollector(AsyncCollectorBase):
    collector_type = CollectorType.INTERNET_ARCHIVE
    preprocessor = InternetArchivePreprocessor

    async def run_implementation(self) -> None:
        await self.log("Running Internet Archive Crawler...")
        dto: InternetArchiveInputDTO = self.dto
        crawler = InternetArchiveCrawler(
            urls=dto.urls,
            max_results_per_domain=dto.max_results_per_domain,
            exclude_patterns=dto.exclude_patterns,
            mime_type_allowlist=dto.mime_type_allowlist,
        )
        async for status in crawler.run():
            await self.log(status)

        self.data = {"results": [r.model_dump() for r in crawler.results]}
