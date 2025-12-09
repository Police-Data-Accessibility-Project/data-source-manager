"""
The task loader loads task a task operator and all dependencies.
"""

from environs import Env

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.core import DSAppSyncAgenciesAddTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.core import DSAppSyncAgenciesDeleteTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.core import DSAppSyncDataSourcesAddTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.core import \
    DSAppSyncDataSourcesDeleteTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.core import \
    DSAppSyncDataSourcesUpdateTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.core import DSAppSyncMetaURLsAddTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.core import DSAppSyncMetaURLsDeleteTaskOperator
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.core import DSAppSyncMetaURLsUpdateTaskOperator
from src.core.tasks.url.models.entry import URLTaskEntry
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.core.tasks.url.operators.auto_name.core import AutoNameURLTaskOperator
from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.core.tasks.url.operators.location_id.core import LocationIdentificationTaskOperator
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.core import NLPProcessor
from src.core.tasks.url.operators.location_id.subtasks.loader import LocationIdentificationSubtaskLoader
from src.core.tasks.url.operators.misc_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.core.tasks.url.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier
from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.core.tasks.url.operators.screenshot.core import URLScreenshotTaskOperator
from src.core.tasks.url.operators.suspend.core import SuspendURLTaskOperator
from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.pdap.client import PDAPClient
from src.external.url_request.core import URLRequestInterface


class URLTaskOperatorLoader:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser,
            pdap_client: PDAPClient,
            muckrock_api_interface: MuckrockAPIInterface,
            hf_inference_client: HuggingFaceInferenceClient,
            nlp_processor: NLPProcessor
    ):
        # Dependencies
        self.adb_client = adb_client
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser
        self.nlp_processor = nlp_processor
        self.env = Env()

        # External clients and interfaces
        self.pdap_client = pdap_client
        self.muckrock_api_interface = muckrock_api_interface
        self.hf_inference_client = hf_inference_client

    def setup_flag(self, name: str) -> bool:
        return self.env.bool(
            name,
            default=True
        )

    def _get_url_html_task_operator(self) -> URLTaskEntry:
        operator = URLHTMLTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_HTML_TASK_FLAG")
        )

    def _get_url_record_type_task_operator(self) -> URLTaskEntry:
        operator = URLRecordTypeTaskOperator(
            adb_client=self.adb_client,
            classifier=OpenAIRecordClassifier()
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_RECORD_TYPE_TASK_FLAG")
        )

    def _get_agency_identification_task_operator(self) -> URLTaskEntry:
        operator = AgencyIdentificationTaskOperator(
            adb_client=self.adb_client,
            loader=AgencyIdentificationSubtaskLoader(
                pdap_client=self.pdap_client,
                muckrock_api_interface=self.muckrock_api_interface,
                adb_client=self.adb_client,
            )
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_AGENCY_IDENTIFICATION_TASK_FLAG")
        )

    def _get_url_miscellaneous_metadata_task_operator(self) -> URLTaskEntry:
        operator = URLMiscellaneousMetadataTaskOperator(
            adb_client=self.adb_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_MISC_METADATA_TASK_FLAG")
        )


    def _get_url_auto_relevance_task_operator(self) -> URLTaskEntry:
        operator = URLAutoRelevantTaskOperator(
            adb_client=self.adb_client,
            hf_client=self.hf_inference_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_AUTO_RELEVANCE_TASK_FLAG")
        )

    def _get_url_probe_task_operator(self) -> URLTaskEntry:
        operator = URLProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_PROBE_TASK_FLAG")
        )

    def _get_url_root_url_task_operator(self) -> URLTaskEntry:
        operator = URLRootURLTaskOperator(
            adb_client=self.adb_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_ROOT_URL_TASK_FLAG")
        )

    def _get_url_screenshot_task_operator(self) -> URLTaskEntry:
        operator = URLScreenshotTaskOperator(
            adb_client=self.adb_client,
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_SCREENSHOT_TASK_FLAG")
        )

    def _get_location_id_task_operator(self) -> URLTaskEntry:
        operator = LocationIdentificationTaskOperator(
            adb_client=self.adb_client,
            loader=LocationIdentificationSubtaskLoader(
                adb_client=self.adb_client,
                nlp_processor=self.nlp_processor
            )
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_LOCATION_IDENTIFICATION_TASK_FLAG")
        )

    def _get_auto_validate_task_operator(self) -> URLTaskEntry:
        operator = AutoValidateURLTaskOperator(
            adb_client=self.adb_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_AUTO_VALIDATE_TASK_FLAG")
        )

    def _get_auto_name_task_operator(self) -> URLTaskEntry:
        operator = AutoNameURLTaskOperator(
            adb_client=self.adb_client,
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_AUTO_NAME_TASK_FLAG")
        )

    def _get_suspend_url_task_operator(self) -> URLTaskEntry:
        operator = SuspendURLTaskOperator(
            adb_client=self.adb_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("URL_SUSPEND_TASK_FLAG")
        )

    # DS App Sync
    ## Agency
    ### Add
    def _get_ds_app_sync_agency_add_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncAgenciesAddTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_AGENCY_ADD_TASK_FLAG")
        )

    ### Update
    def _get_ds_app_sync_agency_update_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncAgenciesUpdateTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_AGENCY_UPDATE_TASK_FLAG")
        )

    ### Delete
    def _get_ds_app_sync_agency_delete_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncAgenciesDeleteTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_AGENCY_DELETE_TASK_FLAG")
        )

    ## Data Source
    ### Add
    def _get_ds_app_sync_data_source_add_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncDataSourcesAddTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_DATA_SOURCE_ADD_TASK_FLAG")
        )

    ### Update
    def _get_ds_app_sync_data_source_update_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncDataSourcesUpdateTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_DATA_SOURCE_UPDATE_TASK_FLAG")
        )

    ### Delete
    def _get_ds_app_sync_data_source_delete_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncDataSourcesDeleteTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_DATA_SOURCE_DELETE_TASK_FLAG")
        )

    ## Meta URL
    ### Add
    def _get_ds_app_sync_meta_url_add_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncMetaURLsAddTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_META_URL_ADD_TASK_FLAG")
        )

    ### Update
    def _get_ds_app_sync_meta_url_update_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncMetaURLsUpdateTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_META_URL_UPDATE_TASK_FLAG")
        )

    ### Delete
    def _get_ds_app_sync_meta_url_delete_task_operator(self) -> URLTaskEntry:
        operator = DSAppSyncMetaURLsDeleteTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.setup_flag("DS_APP_SYNC_META_URL_DELETE_TASK_FLAG")
        )


    async def load_entries(self) -> list[URLTaskEntry]:
        return [
            self._get_url_root_url_task_operator(),
            self._get_url_probe_task_operator(),
            self._get_url_html_task_operator(),
            self._get_url_record_type_task_operator(),
            self._get_agency_identification_task_operator(),
            self._get_url_miscellaneous_metadata_task_operator(),
            self._get_url_auto_relevance_task_operator(),
            self._get_url_screenshot_task_operator(),
            self._get_location_id_task_operator(),
            self._get_auto_validate_task_operator(),
            self._get_auto_name_task_operator(),
            self._get_suspend_url_task_operator(),
            # DS App Sync
            ## Agency
            self._get_ds_app_sync_agency_add_task_operator(),
            self._get_ds_app_sync_agency_update_task_operator(),
            self._get_ds_app_sync_agency_delete_task_operator(),
            ## Data Source
            self._get_ds_app_sync_data_source_add_task_operator(),
            self._get_ds_app_sync_data_source_update_task_operator(),
            self._get_ds_app_sync_data_source_delete_task_operator(),
            ## Meta URL
            self._get_ds_app_sync_meta_url_add_task_operator(),
            self._get_ds_app_sync_meta_url_update_task_operator(),
            self._get_ds_app_sync_meta_url_delete_task_operator(),
        ]
