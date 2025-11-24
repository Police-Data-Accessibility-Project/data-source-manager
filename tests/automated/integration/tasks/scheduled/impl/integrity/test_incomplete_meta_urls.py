import pytest

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator
):
    pass

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add Meta URL without linking an agency to it

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_error=""
    )

    # Add agency to Meta URL

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()


