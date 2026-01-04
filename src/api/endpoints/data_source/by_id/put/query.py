from sqlalchemy import update, select, literal, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.data_source.by_id.put.request import DataSourcePutRequest
from src.api.shared.batch.url.link import UpdateBatchURLLinkQueryBuilder
from src.api.shared.record_type.put.query import UpdateRecordTypeQueryBuilder
from src.api.shared.url.put.query import UpdateURLQueryBuilder
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.queries.base.builder import QueryBuilderBase


class UpdateDataSourceQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        request: DataSourcePutRequest,
    ):
        super().__init__()
        self.url_id = url_id
        self.request = request

    async def run(self, session: AsyncSession) -> None:

        if self.request.record_type is not None:
            await UpdateRecordTypeQueryBuilder(
                url_id=self.url_id,
                record_type=self.request.record_type
            ).run(session)

        # Update URL if any of the URL fields are not None
        if (
            self.request.description is None and
            self.request.name is None and
            self.request.description is None
        ):
            return

        # Update Batch if Batch link is none
        if self.request.batch_id is not None:
            await UpdateBatchURLLinkQueryBuilder(
                batch_id=self.request.batch_id,
                url_id=self.url_id
            ).run(session)

        await UpdateURLQueryBuilder(
            url_id=self.url_id,
            url=self.request.url,
            name=self.request.name,
            description=self.request.description,
        ).run(
            session,
        )
        if not self.request.optional_data_source_metadata_not_none():
            return
        value_dict = {}
        if self.request.record_formats is not None:
            value_dict["record_formats"] = self.request.record_formats
        if self.request.data_portal_type is not None:
            value_dict["data_portal_type"] = self.request.data_portal_type
        if self.request.supplying_entity is not None:
            value_dict["supplying_entity"] = self.request.supplying_entity
        if self.request.coverage_start is not None:
            value_dict["coverage_start"] = self.request.coverage_start
        if self.request.coverage_end is not None:
            value_dict["coverage_end"] = self.request.coverage_end
        if self.request.agency_supplied is not None:
            value_dict["agency_supplied"] = self.request.agency_supplied
        if self.request.agency_originated is not None:
            value_dict["agency_originated"] = self.request.agency_originated
        if self.request.agency_aggregation is not None:
            value_dict["agency_aggregation"] = self.request.agency_aggregation
        if self.request.agency_described_not_in_database is not None:
            value_dict["agency_described_not_in_database"] = self.request.agency_described_not_in_database
        if self.request.update_method is not None:
            value_dict["update_method"] = self.request.update_method
        if self.request.readme_url is not None:
            value_dict["readme_url"] = self.request.readme_url
        if self.request.originating_entity is not None:
            value_dict["originating_entity"] = self.request.originating_entity
        if self.request.retention_schedule is not None:
            value_dict["retention_schedule"] = self.request.retention_schedule
        if self.request.scraper_url is not None:
            value_dict["scraper_url"] = self.request.scraper_url
        if self.request.submission_notes is not None:
            value_dict["submission_notes"] = self.request.submission_notes
        if self.request.access_notes is not None:
            value_dict["access_notes"] = self.request.access_notes
        if self.request.access_types is not None:
            value_dict["access_types"] = self.request.access_types

        # Check for existing metadata object
        query = (
            select(
                literal(True)
            )
            .where(
                URLOptionalDataSourceMetadata.url_id == self.url_id
            )
        )
        exists = await self.sh.one_or_none(session=session, query=query)
        if not exists:
            insert_obj = URLOptionalDataSourceMetadata(
                url_id=self.url_id,
                **value_dict
            )
            session.add(insert_obj)
        else:
            statement = (
                update(
                    URLOptionalDataSourceMetadata
                )
                .where(
                    URLOptionalDataSourceMetadata.url_id == self.url_id
                )
                .values(
                    value_dict
                )
            )

            await session.execute(statement)


