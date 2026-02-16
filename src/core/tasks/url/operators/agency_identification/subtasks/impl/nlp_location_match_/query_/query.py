from collections import defaultdict
from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput, LocationAnnotationToAgencyIDMapping, LocationAnnotation
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.nlp_location import \
    NLP_LOCATION_CONTAINER
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetAgenciesLinkedToAnnotatedLocationsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[NLPLocationMatchSubtaskInput]:
        query = (
            select(
                NLP_LOCATION_CONTAINER.url_id,
                AnnotationLocationAutoSuggestion.location_id,
                AnnotationLocationAutoSuggestion.confidence,
                LinkAgencyLocation.agency_id,
            )
            .join(
                AnnotationLocationAutoSubtask,
                AnnotationLocationAutoSubtask.url_id == NLP_LOCATION_CONTAINER.url_id
            )
            .join(
                AnnotationLocationAutoSuggestion,
                AnnotationLocationAutoSuggestion.subtask_id == AnnotationLocationAutoSubtask.id
            )
            .join(
                LinkAgencyLocation,
                LinkAgencyLocation.location_id == AnnotationLocationAutoSuggestion.location_id
            )
            .where(
                ~NLP_LOCATION_CONTAINER.entry_exists
            )
        )

        url_id_to_location_id_to_agency_ids: dict[int, dict[int, list[int]]] = defaultdict(
            lambda: defaultdict(list)
        )
        url_id_to_location_id_to_annotations: dict[int, dict[int, LocationAnnotation]] = defaultdict(dict)

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        for mapping in mappings:
            url_id: int = mapping["id"]
            location_id: int = mapping["location_id"]
            confidence: int = mapping["confidence"]
            agency_id: int = mapping["agency_id"]

            if agency_id is None:
                continue
            url_id_to_location_id_to_agency_ids[url_id][location_id].append(agency_id)
            if location_id not in url_id_to_location_id_to_annotations[url_id]:
                location_annotation = LocationAnnotation(
                    location_id=location_id,
                    confidence=confidence,
                )
                url_id_to_location_id_to_annotations[url_id][location_id] = location_annotation

        results: list[NLPLocationMatchSubtaskInput] = []
        for url_id in url_id_to_location_id_to_agency_ids:
            anno_mappings: list[LocationAnnotationToAgencyIDMapping] = []
            for location_id in url_id_to_location_id_to_agency_ids[url_id]:
                location_annotation: LocationAnnotation = url_id_to_location_id_to_annotations[url_id][location_id]
                agency_ids: list[int] = url_id_to_location_id_to_agency_ids[url_id][location_id]
                anno_mapping: LocationAnnotationToAgencyIDMapping = LocationAnnotationToAgencyIDMapping(
                    location_annotation=location_annotation,
                    agency_ids=agency_ids,
                )
                anno_mappings.append(anno_mapping)
            input_ = NLPLocationMatchSubtaskInput(
                url_id=url_id,
                mappings=anno_mappings,
            )
            results.append(input_)
        return results

