from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.agency import AgencyValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.location import LocationValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.record_type import \
    RecordTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.url_type import URLTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.helper import add_where_condition
from src.db.helpers.session import session_helper as sh
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.queries.base.builder import QueryBuilderBase


class AutoValidatePrerequisitesQueryBuilder(QueryBuilderBase):
    """
    Checks to see if any URL meets any of the following prerequisites
    - Is a DATA SOURCE URL with consensus on all fields
    - Is a META URL with consensus on url_type, agency, and location fields
    - Is a NOT RELEVANT or SINGLE PAGE URL with consensus on url_type
    """

    async def run(self, session: AsyncSession) -> bool:
        agency = AgencyValidationCTEContainer()
        location = LocationValidationCTEContainer()
        url_type = URLTypeValidationCTEContainer()
        record_type = RecordTypeValidationCTEContainer()


        query = (
            select(
                UnvalidatedURL.url_id,
            )
            .select_from(
                UnvalidatedURL
            )
            .outerjoin(
                agency.query,
                UnvalidatedURL.url_id == agency.url_id,
            )
            .outerjoin(
                location.query,
                UnvalidatedURL.url_id == location.url_id,
            )
            .outerjoin(
                url_type.query,
                UnvalidatedURL.url_id == url_type.url_id,
            )
            .outerjoin(
                record_type.query,
                UnvalidatedURL.url_id == record_type.url_id,
            )
        )
        query = add_where_condition(
            query,
            agency=agency,
            location=location,
            url_type=url_type,
            record_type=record_type,
        ).limit(1)

        return await sh.results_exist(session, query=query)


