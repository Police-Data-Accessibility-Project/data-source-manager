import spacy

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan_.core import CKANAgencyIDSubtaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.core import \
    HomepageMatchSubtaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock_.core import \
    MuckrockAgencyIDSubtaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.core import \
    NLPLocationMatchSubtaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.core import \
    NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.external.pdap.client import PDAPClient


class AgencyIdentificationSubtaskLoader:
    """Loads subtasks and associated dependencies."""

    def __init__(
        self,
        pdap_client: PDAPClient,
        muckrock_api_interface: MuckrockAPIInterface,
        adb_client: AsyncDatabaseClient
    ):
        self._pdap_client = pdap_client
        self._muckrock_api_interface = muckrock_api_interface
        self.adb_client = adb_client

    def _load_muckrock_subtask(self, task_id: int) -> MuckrockAgencyIDSubtaskOperator:
        return MuckrockAgencyIDSubtaskOperator(
            task_id=task_id,
            adb_client=self.adb_client,
            muckrock_api_interface=self._muckrock_api_interface,
            pdap_client=self._pdap_client
        )

    def _load_ckan_subtask(self, task_id: int) -> CKANAgencyIDSubtaskOperator:
        return CKANAgencyIDSubtaskOperator(
            task_id=task_id,
            adb_client=self.adb_client,
            pdap_client=self._pdap_client
        )

    def _load_homepage_match_subtask(self, task_id: int) -> HomepageMatchSubtaskOperator:
        return HomepageMatchSubtaskOperator(
            task_id=task_id,
            adb_client=self.adb_client,
        )

    def _load_nlp_location_match_subtask(self, task_id: int) -> NLPLocationMatchSubtaskOperator:
        return NLPLocationMatchSubtaskOperator(
            task_id=task_id,
            adb_client=self.adb_client,
            pdap_client=self._pdap_client,
            processor=NLPProcessor(
                spacy.load('en_core_web_trf', disable=['parser'])
            )
        )


    async def load_subtask(
        self,
        subtask_type: AutoAgencyIDSubtaskType,
        task_id: int
    ) -> AgencyIDSubtaskOperatorBase:
        """Get subtask based on collector type."""
        match subtask_type:
            case AutoAgencyIDSubtaskType.MUCKROCK:
                return self._load_muckrock_subtask(task_id)
            case AutoAgencyIDSubtaskType.CKAN:
                return self._load_ckan_subtask(task_id)
            case AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH:
                return self._load_muckrock_subtask(task_id)
            case AutoAgencyIDSubtaskType.HOMEPAGE_MATCH:
                return self._load_homepage_match_subtask(task_id)
        raise ValueError(f"Unknown subtask type: {subtask_type}")
