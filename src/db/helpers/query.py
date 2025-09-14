from sqlalchemy import exists, ColumnElement

from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.mixins import URLDependentMixin


def url_not_validated() -> ColumnElement[bool]:
    return not_exists_url(FlagURLValidated)

def not_exists_url(
    model: type[URLDependentMixin]
) -> ColumnElement[bool]:
    return ~exists().where(
        model.url_id == URL.id
    )