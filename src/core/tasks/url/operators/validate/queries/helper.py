from sqlalchemy import Select, or_, and_

from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.agency import AgencyValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.location import LocationValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.name import NameValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.record_type import \
    RecordTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.url_type import URLTypeValidationCTEContainer
from src.db.models.impl.flag.url_validated.enums import URLType


def add_where_condition(
    query: Select,
    agency: AgencyValidationCTEContainer,
    location: LocationValidationCTEContainer,
    url_type: URLTypeValidationCTEContainer,
    record_type: RecordTypeValidationCTEContainer,
    name: NameValidationCTEContainer,
) -> Select:
    return (
        query
        .where(
            url_type.url_type.isnot(None),
            or_(
                and_(
                    url_type.url_type == URLType.DATA_SOURCE.value,
                    agency.agency_id.isnot(None),
                    location.location_id.isnot(None),
                    record_type.record_type.isnot(None),
                    name.name.isnot(None),
                ),
                and_(
                    url_type.url_type.in_(
                        (URLType.META_URL.value, URLType.INDIVIDUAL_RECORD.value)
                    ),
                    agency.agency_id.isnot(None),
                    location.location_id.isnot(None),
                    name.name.isnot(None),
                ),
                url_type.url_type == URLType.NOT_RELEVANT.value
                ),
            )
        )
