from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.core import \
    NLPLocationFrequencySubtaskOperator
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.core import NLPProcessor
from src.core.tasks.url.operators.location_id.subtasks.templates.subtask import LocationIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType


class LocationIdentificationSubtaskLoader:
    """Loads subtasks and associated dependencies."""

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        nlp_processor: NLPProcessor,
    ):
        self.adb_client = adb_client
        self._nlp_processor = nlp_processor

    def _load_nlp_location_match_subtask(self, task_id: int) -> NLPLocationFrequencySubtaskOperator:
        return NLPLocationFrequencySubtaskOperator(
            task_id=task_id,
            adb_client=self.adb_client,
            nlp_processor=self._nlp_processor
        )

    async def load_subtask(
        self,
        subtask_type: LocationIDSubtaskType,
        task_id: int
    ) -> LocationIDSubtaskOperatorBase:
        match subtask_type:
            case LocationIDSubtaskType.NLP_LOCATION_FREQUENCY:
                return self._load_nlp_location_match_subtask(task_id=task_id)
        raise ValueError(f"Unknown subtask type: {subtask_type}")
