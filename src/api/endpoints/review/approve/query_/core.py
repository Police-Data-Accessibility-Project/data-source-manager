from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.approve.query_.util import update_if_not_none
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.impl.url.reviewing_user import ReviewingUserURL
from src.db.queries.base.builder import QueryBuilderBase


class ApproveURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        approval_info: FinalReviewApprovalInfo
    ):
        super().__init__()
        self.user_id = user_id
        self.approval_info = approval_info

    async def run(self, session: AsyncSession) -> None:
        # Get URL

        url = await self._get_url(session)

        await self._optionally_update_record_type(session)

        # Get existing agency ids
        existing_agencies = url.confirmed_agencies or []
        existing_agency_ids = [agency.agency_id for agency in existing_agencies]
        new_agency_ids = self.approval_info.agency_ids or []
        await self._check_for_unspecified_agency_ids(existing_agency_ids, new_agency_ids)

        await self._overwrite_existing_agencies(existing_agencies, new_agency_ids, session)
        # Add any new agency ids that are not in the existing agency ids
        await self._add_new_agencies(existing_agency_ids, new_agency_ids, session)

        await self._add_validated_flag(session, url=url)

        await self._optionally_update_required_metadata(url)
        await self._optionally_update_optional_metdata(url)
        await self._add_approving_user(session)

    async def _optionally_update_required_metadata(self, url: URL) -> None:
        update_if_not_none(url, "name", self.approval_info.name, required=True)
        update_if_not_none(url, "description", self.approval_info.description, required=False)

    async def _add_approving_user(self, session: AsyncSession) -> None:
        approving_user_url = ReviewingUserURL(
            user_id=self.user_id,
            url_id=self.approval_info.url_id
        )
        session.add(approving_user_url)

    async def _optionally_update_optional_metdata(self, url: URL) -> None:
        optional_metadata = url.optional_data_source_metadata
        if optional_metadata is None:
            url.optional_data_source_metadata = URLOptionalDataSourceMetadata(
                record_formats=self.approval_info.record_formats,
                data_portal_type=self.approval_info.data_portal_type,
                supplying_entity=self.approval_info.supplying_entity
            )
        else:
            update_if_not_none(
                optional_metadata,
                "record_formats",
                self.approval_info.record_formats
            )
            update_if_not_none(
                optional_metadata,
                "data_portal_type",
                self.approval_info.data_portal_type
            )
            update_if_not_none(
                optional_metadata,
                "supplying_entity",
                self.approval_info.supplying_entity
            )

    async def _optionally_update_record_type(self, session: AsyncSession) -> None:
        if self.approval_info.record_type is None:
            return

        record_type = URLRecordType(
            url_id=self.approval_info.url_id,
            record_type=self.approval_info.record_type.value
        )
        session.add(record_type)

    async def _get_url(self, session: AsyncSession) -> URL:
        query = (
            Select(URL)
            .where(URL.id == self.approval_info.url_id)
            .options(
                joinedload(URL.optional_data_source_metadata),
                joinedload(URL.confirmed_agencies),
            )
        )
        url = await session.execute(query)
        url = url.scalars().first()
        return url

    async def _check_for_unspecified_agency_ids(
        self,
        existing_agency_ids: list[int],
        new_agency_ids: list[int]
    ) -> None:
        """
        raises:
            HTTPException: If no agency ids are specified and no existing agency ids are found
        """
        if len(existing_agency_ids) == 0 and len(new_agency_ids) == 0:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Must specify agency_id if URL does not already have a confirmed agency"
            )

    async def _overwrite_existing_agencies(self, existing_agencies, new_agency_ids, session):
        # Get any existing agency ids that are not in the new agency ids
        # If new agency ids are specified, overwrite existing
        if len(new_agency_ids) != 0:
            for existing_agency in existing_agencies:
                if existing_agency.id not in new_agency_ids:
                    # If the existing agency id is not in the new agency ids, delete it
                    await session.delete(existing_agency)

    async def _add_new_agencies(self, existing_agency_ids, new_agency_ids, session):
        for new_agency_id in new_agency_ids:
            if new_agency_id in existing_agency_ids:
                continue
            # Check if the new agency exists in the database
            query = (
                select(Agency)
                .where(Agency.agency_id == new_agency_id)
            )
            existing_agency = await session.execute(query)
            existing_agency = existing_agency.scalars().first()
            if existing_agency is None:
                # If not, raise an error
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Agency not found"
                )


            # If the new agency id is not in the existing agency ids, add it
            confirmed_url_agency = LinkURLAgency(
                url_id=self.approval_info.url_id,
                agency_id=new_agency_id
            )
            session.add(confirmed_url_agency)

    async def _add_validated_flag(
        self,
        session: AsyncSession,
        url: URL
    ) -> None:
        flag = FlagURLValidated(
            url_id=url.id,
            type=URLType.DATA_SOURCE
        )
        session.add(flag)
