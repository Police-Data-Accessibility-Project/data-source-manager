from src.core.enums import RecordType
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier
from src.core.tasks.url.operators.record_type.queries.get import GetRecordTypeTaskURLsQueryBuilder
from src.core.tasks.url.operators.record_type.queries.prereq import RecordTypeTaskPrerequisiteQueryBuilder
from src.core.tasks.url.operators.record_type.tdo import URLRecordTypeTDO
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.with_html import URLWithHTML
from src.db.enums import TaskType
from src.db.models.impl.annotation.record_type.auto.sqlalchemy import AnnotationAutoRecordType
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall


class URLRecordTypeTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            classifier: OpenAIRecordClassifier
    ):
        super().__init__(adb_client)
        self.classifier = classifier

    @property
    def task_type(self) -> TaskType:
        return TaskType.RECORD_TYPE

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            RecordTypeTaskPrerequisiteQueryBuilder()
        )

    async def get_tdos(self) -> list[URLRecordTypeTDO]:
        urls_with_html: list[URLWithHTML] = await self.run_query_builder(
            GetRecordTypeTaskURLsQueryBuilder()
        )
        tdos = [URLRecordTypeTDO(url_with_html=url_with_html) for url_with_html in urls_with_html]
        return tdos

    async def inner_task_logic(self) -> None:
        # Get pending urls from Source Collector
        # with HTML data and without Record Type Metadata
        tdos = await self.get_tdos()
        url_ids = [tdo.url_with_html.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)

        await self.get_ml_classifications(tdos)
        success_subset, error_subset = await self.separate_success_and_error_subsets(tdos)
        await self.put_results_into_database(success_subset)
        await self.update_errors_in_database(error_subset)

    async def update_errors_in_database(
        self,
        tdos: list[URLRecordTypeTDO]
    ) -> None:
        task_errors: list[URLTaskErrorSmall] = []
        for tdo in tdos:
            error_info = URLTaskErrorSmall(
                url_id=tdo.url_with_html.url_id,
                error=tdo.error
            )
            task_errors.append(error_info)
        await self.add_task_errors(task_errors)

    async def put_results_into_database(
        self,
        tdos: list[URLRecordTypeTDO]
    ) -> None:
        url_and_record_type_list = []
        for tdo in tdos:
            url_id = tdo.url_with_html.url_id
            record_type = tdo.record_type
            url_and_record_type_list.append((url_id, record_type))
        # Add to database
        suggestions: list[AnnotationAutoRecordType] = []
        for url_id, record_type in url_and_record_type_list:
            suggestion = AnnotationAutoRecordType(
                url_id=url_id,
                record_type=record_type.value
            )
            suggestions.append(suggestion)
        await self.adb_client.add_all(suggestions)

    @staticmethod
    async def separate_success_and_error_subsets(
        tdos: list[URLRecordTypeTDO]
    ) -> tuple[list[URLRecordTypeTDO], list[URLRecordTypeTDO]]:
        success_subset = [tdo for tdo in tdos if not tdo.is_errored()]
        error_subset = [tdo for tdo in tdos if tdo.is_errored()]
        return success_subset, error_subset

    async def get_ml_classifications(
        self,
        tdos: list[URLRecordTypeTDO]
    ) -> None:
        """
        Modifies:
        - tdo.record_type
        - tdo.error
        """
        for tdo in tdos:
            try:
                record_type_str = await self.classifier.classify_url(tdo.url_with_html.html_infos)
                tdo.record_type = RecordType(record_type_str)
            except Exception as e:
                tdo.error = str(e)