from src.core.tasks.url.operators.auto_name.clean import clean_title
from src.core.tasks.url.operators.auto_name.input import AutoNamePrerequisitesInput
from src.core.tasks.url.operators.auto_name.queries.get import AutoNameGetInputsQueryBuilder
from src.core.tasks.url.operators.auto_name.queries.prereq import AutoNamePrerequisitesQueryBuilder
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.enums import TaskType
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.pydantic import URLNameSuggestionPydantic


class AutoNameURLTaskOperator(URLTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.AUTO_NAME

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            AutoNamePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:

        # Get URLs with HTML metadata title
        inputs: list[AutoNamePrerequisitesInput] = await self.adb_client.run_query_builder(
            AutoNameGetInputsQueryBuilder()
        )

        # Link URLs to task
        url_ids: list[int] = [input.url_id for input in inputs]
        await self.link_urls_to_task(url_ids)

        # Add suggestions
        suggestions: list[URLNameSuggestionPydantic] = [
            URLNameSuggestionPydantic(
                url_id=input_.url_id,
                suggestion=clean_title(input_.title),
                source=NameSuggestionSource.HTML_METADATA_TITLE,
            )
            for input_ in inputs
        ]

        await self.adb_client.bulk_insert(models=suggestions)

