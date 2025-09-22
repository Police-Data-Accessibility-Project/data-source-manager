import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator

@pytest.fixture
def operator() -> AutoValidateURLTaskOperator:
    raise NotImplementedError