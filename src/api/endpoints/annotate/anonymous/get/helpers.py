from typing import Protocol, TypeVar
from uuid import UUID

from marshmallow.fields import Bool
from sqlalchemy import Exists, select, exists, ColumnElement, Boolean

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.mixins import AnonymousSessionMixin, URLDependentMixin
from src.db.models.templates_.base import Base


class AnonymousURLModelProtocol(
    Protocol,
):
    session_id: ColumnElement[UUID]
    url_id: ColumnElement[int]

AnonModel = TypeVar("AnonModel", bound=AnonymousURLModelProtocol)

def not_exists_anon_annotation(session_id: UUID, anon_model: AnonModel) -> ColumnElement[bool]:
    return ~exists(
        select(anon_model.url_id)
        .where(
            anon_model.url_id == URL.id,
            anon_model.session_id == session_id,
        )
    )