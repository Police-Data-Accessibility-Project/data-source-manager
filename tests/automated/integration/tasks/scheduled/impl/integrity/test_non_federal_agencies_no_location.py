import pytest

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator
):
    pass

    # Check does not meet prerequisites

    # Add federal agency

    # Check does not meet prerequisites

    # Add non-federal agency

    # Check meets prerequisites

    # Run task and confirm produces error

    # Add location to non-federal agency

    # Check no longer meets task prerequisites
