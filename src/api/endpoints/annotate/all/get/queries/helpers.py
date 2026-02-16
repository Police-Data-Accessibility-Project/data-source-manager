from typing import Protocol, TypeVar

from sqlalchemy import ColumnElement, select, exists

from src.db.models.impl.url.core.sqlalchemy import URL


class UserURLModelProtocol(
    Protocol,
):
    user_id: ColumnElement[int]
    url_id: ColumnElement[int]

UserModel = TypeVar("UserModel", bound=UserURLModelProtocol)

def not_exists_user_annotation(
    user_id: int,
    user_model: UserModel
) -> ColumnElement[bool]:
    return ~exists(
        select(user_model.url_id)
        .where(
            user_model.url_id == URL.id,
            user_model.user_id == user_id,
        )
    )