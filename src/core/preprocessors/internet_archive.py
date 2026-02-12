from typing import List

from src.core.preprocessors.base import PreprocessorBase
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


class InternetArchivePreprocessor(PreprocessorBase):

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for domain_result in data["results"]:
            for url_entry in domain_result["urls"]:
                url_infos.append(URLInfo(
                    url=url_entry["url"],
                    collector_metadata={
                        "source_domain": domain_result["domain"],
                        "archive_url": url_entry["archive_url"],
                        "ia_timestamp": url_entry["timestamp"],
                        "ia_digest": url_entry["digest"],
                    },
                    source=URLSource.COLLECTOR,
                ))
        return url_infos
