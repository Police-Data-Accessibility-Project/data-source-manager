from typing import Any

from src.collectors.impl.auto_googler.queries.agency import AutoGooglerAddAgencyQueryBuilder
from src.collectors.impl.auto_googler.queries.location import AutoGooglerAddLocationQueryBuilder
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.enums import CollectorType
from src.core.env_var_manager import EnvVarManager
from src.core.preprocessors.autogoogler import AutoGooglerPreprocessor
from src.collectors.impl.auto_googler.auto_googler import AutoGoogler
from src.collectors.impl.auto_googler.dtos.output import AutoGooglerInnerOutputDTO
from src.collectors.impl.auto_googler.dtos.input import AutoGooglerInputDTO
from src.collectors.impl.auto_googler.searcher import GoogleSearcher
from src.collectors.impl.auto_googler.dtos.config import SearchConfig
from src.db.models.impl.link.agency_batch.sqlalchemy import LinkAgencyBatch
from src.util.helper_functions import base_model_list_dump


class AutoGooglerCollector(AsyncCollectorBase):
    collector_type = CollectorType.AUTO_GOOGLER
    preprocessor = AutoGooglerPreprocessor

    async def run_to_completion(self) -> AutoGoogler:
        dto: AutoGooglerInputDTO = self.dto

        queries: list[str] = dto.queries.copy()

        if dto.agency_id is not None:

            agency_name: str = await self.adb_client.run_query_builder(
                AutoGooglerAddAgencyQueryBuilder(
                    batch_id=self.batch_id,
                    agency_id=dto.agency_id,
                )
            )

            # Add to all queries
            queries = [f"{query} {agency_name}" for query in queries]

        if dto.location_id is not None:
            location_name: str = await self.adb_client.run_query_builder(
                AutoGooglerAddLocationQueryBuilder(
                    batch_id=self.batch_id,
                    location_id=dto.location_id,
                )
            )

            # Add to all queries
            queries = [f"{query} {location_name}" for query in queries]

        env_var_manager = EnvVarManager.get()
        auto_googler = AutoGoogler(
            search_config=SearchConfig(
                urls_per_result=dto.urls_per_result,
                queries=queries,
            ),
            google_searcher=GoogleSearcher(
                api_key=env_var_manager.google_api_key,
                cse_id=env_var_manager.google_cse_id,
            )
        )
        async for log in auto_googler.run():
            await self.log(log)
        return auto_googler

    async def run_implementation(self) -> None:

        auto_googler: AutoGoogler = await self.run_to_completion()

        inner_data: list[dict[str, Any]] = []
        for query in auto_googler.search_config.queries:
            query_results: list[AutoGooglerInnerOutputDTO] = auto_googler.data[query]
            inner_data.append({
                "query": query,
                "query_results": base_model_list_dump(query_results),
            })

        self.data = {"data": inner_data}

