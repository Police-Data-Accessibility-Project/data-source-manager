from unittest.mock import AsyncMock

from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput


def check_results_called(
    operator: PushToHuggingFaceTaskOperator,
    expected_outputs: list[GetForLoadingToHuggingFaceOutput]
) -> None:
    mock_hf_client: AsyncMock = operator.hf_client
    mock_push: AsyncMock = mock_hf_client.push_data_sources_raw_to_hub
    outputs: list[GetForLoadingToHuggingFaceOutput] = mock_push.call_args.args[0]
    outputs = sorted(outputs, key=lambda x: x.url_id)
    expected_outputs = sorted(expected_outputs, key=lambda x: x.url_id)
    for output, expected_output in zip(outputs, expected_outputs):
        assert output.url_id == expected_output.url_id
        assert output.url == expected_output.url
        assert output.relevant == expected_output.relevant, f"Expected {expected_output.relevant}, got {output.relevant}"
        assert output.record_type_fine == expected_output.record_type_fine
        assert output.record_type_coarse == expected_output.record_type_coarse
        assert output.html == expected_output.html


def check_not_called(
    operator: PushToHuggingFaceTaskOperator,
) -> None:
    mock_hf_client: AsyncMock = operator.hf_client
    mock_push: AsyncMock =  mock_hf_client.push_data_sources_raw_to_hub
    mock_push.assert_not_called()