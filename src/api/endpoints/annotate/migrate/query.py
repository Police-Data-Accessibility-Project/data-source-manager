from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.models.impl.annotation.name.user.sqlalchemy import AnnotationNameUserEndorsement
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.queries.base.builder import QueryBuilderBase


class MigrateAnonymousAnnotationsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        session_id: UUID,
        user_id: int
    ):
        super().__init__()
        self.session_id = session_id
        self.user_id = user_id

    async def run(self, session: AsyncSession) -> Any:
        await self.migrate_agency_annotations(session)
        await self.migrate_location_annotations(session)
        await self.migrate_record_type_annotations(session)
        await self.migrate_url_type_annotations(session)
        await self.migrate_name_annotations(session)

    async def migrate_agency_annotations(self, session: AsyncSession) -> None:
        # Copy all agency annotations from anonymous to user.
        statement = insert(AnnotationAgencyUser).from_select(
            ["agency_id", "url_id", "user_id"],
            select(
                AnnotationAgencyAnon.agency_id,
                AnnotationAgencyAnon.url_id,
                self.user_id
            ).where(
                AnnotationAgencyAnon.session_id == self.session_id
            )
        )
        await session.execute(statement)
        # Delete all anonymous agency annotations.
        statement = delete(AnnotationAgencyAnon).where(
            AnnotationAgencyAnon.session_id == self.session_id
        )
        await session.execute(statement)


    async def migrate_location_annotations(self, session: AsyncSession) -> None:
        # Copy all location annotations from anonymous to user.
        statement = insert(AnnotationLocationUser).from_select(
            ['location_id', 'url_id', 'user_id'],
            select(
                AnnotationLocationAnon.location_id,
                AnnotationLocationAnon.url_id,
                self.user_id
            ).where(
                AnnotationLocationAnon.session_id == self.session_id
            )
        )
        await session.execute(statement)
        # Delete all anonymous location annotations.
        statement = delete(AnnotationLocationAnon).where(
            AnnotationLocationAnon.session_id == self.session_id
        )
        await session.execute(statement)

    async def migrate_record_type_annotations(self, session: AsyncSession) -> None:
        # Copy all record type annotations from anonymous to user.
        statement = insert(AnnotationRecordTypeUser).from_select(
            ['record_type', 'url_id', 'user_id'],
            select(
                AnnotationRecordTypeAnon.record_type,
                AnnotationRecordTypeAnon.url_id,
                self.user_id
            ).where(
                AnnotationRecordTypeAnon.session_id == self.session_id
            )
        )
        await session.execute(statement)
        # Delete all anonymous record type annotations.
        statement = delete(AnnotationRecordTypeAnon).where(
            AnnotationRecordTypeAnon.session_id == self.session_id
        )
        await session.execute(statement)

    async def migrate_url_type_annotations(self, session: AsyncSession) -> None:
        # Copy all url type annotations from anonymous to user.
        statement = insert(AnnotationURLTypeUser).from_select(
            ['type', 'url_id', 'user_id'],
            select(
                AnnotationURLTypeAnon.url_type,
                AnnotationURLTypeAnon.url_id,
                self.user_id
            ).where(
                AnnotationURLTypeAnon.session_id == self.session_id
            )
        )
        await session.execute(statement)
        # Delete all anonymous url type annotations.
        statement = delete(AnnotationURLTypeAnon).where(
            AnnotationURLTypeAnon.session_id == self.session_id
        )
        await session.execute(statement)

    async def migrate_name_annotations(self, session: AsyncSession) -> None:
        # Copy all name annotations from anonymous to user.
        statement = insert(AnnotationNameUserEndorsement).from_select(
            ['suggestion_id', 'user_id'],
            select(
                AnnotationNameAnonEndorsement.suggestion_id,
                self.user_id
            ).where(
                AnnotationNameAnonEndorsement.session_id == self.session_id
            )
        )
        await session.execute(statement)
        # Delete all anonymous name annotations.
        statement = delete(AnnotationNameAnonEndorsement).where(
            AnnotationNameAnonEndorsement.session_id == self.session_id
        )
        await session.execute(statement)
