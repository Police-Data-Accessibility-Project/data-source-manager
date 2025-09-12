from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.collectors.enums import CollectorType


def convert_strategy_counts_to_strategy_count_dict(
    responses: list[CountByBatchStrategyResponse]
) -> dict[CollectorType, int]:
    result: dict[CollectorType, int] = {collector_type: 0 for collector_type in CollectorType}
    for response in responses:
        result[response.strategy] = response.count
    return result