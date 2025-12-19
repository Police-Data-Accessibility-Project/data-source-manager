from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.convert import \
    convert_params_to_subtask_entries, convert_subtask_mappings_and_params_to_suggestions
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.models.entry import \
    GetHomepageMatchParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.models.mapping import \
    SubtaskURLMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.get import \
    GetHomepageMatchSubtaskURLsQueryBuilder
from src.core.tasks.url.operators.agency_identification.subtasks.templates.subtask import AgencyIDSubtaskOperatorBase
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.annotation.agency.auto.suggestion.pydantic import AgencyIDSubtaskSuggestionPydantic


class HomepageMatchSubtaskOperator(
    AgencyIDSubtaskOperatorBase,
):

    async def inner_logic(self) -> None:
        # Get Params
        params: list[GetHomepageMatchParams] = \
            await self.adb_client.run_query_builder(
                GetHomepageMatchSubtaskURLsQueryBuilder()
            )

        # Insert Subtask Entries
        subtask_entries: list[URLAutoAgencyIDSubtaskPydantic] = convert_params_to_subtask_entries(
            params=params,
            task_id=self.task_id
        )
        subtask_mappings: list[SubtaskURLMapping] = await self.insert_subtask_entries(
            entries=subtask_entries
        )

        # Link URLs
        url_ids: list[int] = [mapping.url_id for mapping in subtask_mappings]
        self.linked_urls = url_ids

        # Insert Entries
        suggestions: list[AgencyIDSubtaskSuggestionPydantic] = convert_subtask_mappings_and_params_to_suggestions(
            mappings=subtask_mappings,
            params=params
        )
        await self.adb_client.bulk_insert(
            models=suggestions,
        )


    async def insert_subtask_entries(
        self,
        entries: list[URLAutoAgencyIDSubtaskPydantic]
    ) -> list[SubtaskURLMapping]:
        subtask_ids: list[int] = await self.adb_client.bulk_insert(
            models=entries,
            return_ids=True
        )
        mappings: list[SubtaskURLMapping] = []
        for subtask_id, entry in zip(subtask_ids, entries):
            mapping = SubtaskURLMapping(
                url_id=entry.url_id,
                subtask_id=subtask_id,
            )
            mappings.append(mapping)
        return mappings
