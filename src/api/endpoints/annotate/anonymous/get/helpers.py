from typing import Protocol, TypeVar
from uuid import UUID

from sqlalchemy import select, exists, ColumnElement

from src.db.models.impl.url.core.sqlalchemy import URL


class AnonymousURLModelProtocol(
    Protocol,
):
    session_id: ColumnElement[UUID]
    url_id: ColumnElement[int]

AnonModel = TypeVar("AnonModel", bound=AnonymousURLModelProtocol)

def not_exists_anon_annotation(
    session_id: UUID,
    anon_model: AnonModel
) -> ColumnElement[bool]:
    return ~exists(
        select(anon_model.url_id)
        .where(
            anon_model.url_id == URL.id,
            anon_model.session_id == session_id,
        )
    )