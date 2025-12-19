import uuid
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.data_source.models.response.standard import SubmitDataSourceURLProposalResponse
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.collectors.enums import URLStatus
from src.core.enums import BatchStatus
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationAnonRecordType
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationAnonURLType
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.anonymous_session import MakeAnonymousSessionQueryBuilder
from src.util.models.full_url import FullURL


class SubmitDataSourceURLProposalQueryBuilder(QueryBuilderBase):

    def __init__(self, request: DataSourceSubmissionRequest):
        super().__init__()
        self.request = request

    async def run(
        self,
        session: AsyncSession
    ) -> SubmitDataSourceURLProposalResponse:
        full_url = FullURL(full_url=self.request.source_url)

        # Begin by attempting to submit the full URL
        url = URL(
            url=full_url.id_form,
            scheme=full_url.scheme,
            trailing_slash=full_url.has_trailing_slash,
            name=self.request.name,
            description=self.request.description,
            status=URLStatus.OK,
            source=URLSource.MANUAL,
        )

        session.add(url)
        await session.flush()

        # Standard Path
        url_id: int = url.id

        # Add Batch
        batch = Batch(
            strategy='manual',
            status=BatchStatus.READY_TO_LABEL,
            parameters={}
        )
        session.add(batch)
        await session.flush()
        batch_id: int = batch.id

        # Add Batch URL link
        batch_url_link = LinkBatchURL(
            batch_id=batch_id,
            url_id=url_id
        )
        session.add(batch_url_link)

        # Create single-use session id
        session_id: uuid.UUID = await MakeAnonymousSessionQueryBuilder().run(session=session)

        # Add URL Type Suggestion
        url_type_suggestion = AnnotationAnonURLType(
            url_id=url_id,
            url_type=URLType.DATA_SOURCE,
            session_id=session_id
        )
        session.add(url_type_suggestion)

        # Optionally add Record Type as suggestion
        if self.request.record_type is not None:
            record_type_suggestion = AnnotationAnonRecordType(
                url_id=url_id,
                record_type=self.request.record_type.value,
                session_id=session_id
            )
            session.add(record_type_suggestion)

        # Optionally add Agency ID suggestions
        if self.request.agency_ids is not None:
            agency_id_suggestions = [
                AnnotationAgencyAnon(
                    url_id=url_id,
                    agency_id=agency_id,
                    session_id=session_id
                )
                for agency_id in self.request.agency_ids
            ]
            session.add_all(agency_id_suggestions)

        # Optionally add Location ID suggestions
        if self.request.location_ids is not None:
            location_id_suggestions = [
                AnnotationLocationAnon(
                    url_id=url_id,
                    location_id=location_id,
                    session_id=session_id
                )
                for location_id in self.request.location_ids
            ]
            session.add_all(location_id_suggestions)

        # Optionally add name suggestion
        if self.request.name is not None:
            name_suggestion = AnnotationNameSuggestion(
                url_id=url_id,
                suggestion=self.request.name,
                source=NameSuggestionSource.USER
            )
            session.add(name_suggestion)

        # Add data source metadata
        ds_metadata = URLOptionalDataSourceMetadata(
            url_id=url_id,
            coverage_start=self.request.coverage_start,
            coverage_end=self.request.coverage_end,
            supplying_entity=self.request.supplying_entity,
            agency_supplied=self.request.agency_supplied,
            agency_originated=self.request.agency_originated,
            agency_aggregation=self.request.agency_aggregation,
            agency_described_not_in_database=self.request.agency_described_not_in_database,
            data_portal_type=self.request.data_portal_type,
            update_method=self.request.update_method,
            readme_url=self.request.readme_url,
            originating_entity=self.request.originating_entity,
            retention_schedule=self.request.retention_schedule,
            scraper_url=self.request.scraper_url,
            submission_notes=self.request.submission_notes,
            access_notes=self.request.access_notes,
            access_types=self.request.access_types,
            record_formats=self.request.record_formats,
        )
        session.add(ds_metadata)
        await session.flush()

        return SubmitDataSourceURLProposalResponse(
            url_id=url_id,
        )