from unittest.mock import MagicMock, AsyncMock


def get_last_call_arguments(mock: MagicMock | AsyncMock) -> tuple:
    return mock.call_args_list[-1].args