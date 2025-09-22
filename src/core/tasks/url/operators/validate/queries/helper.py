from sqlalchemy import Exists, exists, Select, or_, and_

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.agency import AgencyValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.location import LocationValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.record_type import \
    RecordTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.url_type import URLTypeValidationCTEContainer
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.views.unvalidated_url import UnvalidatedURL


def url_exists(cte_container: ValidationCTEContainer) -> Exists:
    return exists().where(
        cte_container.url_id == UnvalidatedURL.url_id,
    )

def add_where_condition(
    query: Select,
    agency: AgencyValidationCTEContainer,
    location: LocationValidationCTEContainer,
    url_type: URLTypeValidationCTEContainer,
    record_type: RecordTypeValidationCTEContainer
) -> Select:
    return (
        query
        .where(
            url_exists(url_type),
            or_(
                and_(
                    url_type.url_type == URLType.DATA_SOURCE.value,
                    url_exists(agency),
                    url_exists(location),
                    url_exists(record_type),
                ),
                and_(
                    url_type.url_type.in_(
                        (URLType.META_URL.value, URLType.INDIVIDUAL_RECORD)
                    ),
                    url_exists(agency),
                    url_exists(location),
                ),
                url_type.url_type == URLType.NOT_RELEVANT.value
                ),
            )
        )
