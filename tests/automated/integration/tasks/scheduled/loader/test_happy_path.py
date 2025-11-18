import pytest

from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader

NUMBER_OF_ENTRIES = 20

@pytest.mark.asyncio
async def test_happy_path(
    loader: ScheduledTaskOperatorLoader,
    monkeypatch
):
    """
    Under normal circumstances, all task operators should be returned
    """
    monkeypatch.setenv("SCHEDULED_TASKS_FLAG", "1")
    entries = await loader.load_entries()
    assert len(entries) == NUMBER_OF_ENTRIES