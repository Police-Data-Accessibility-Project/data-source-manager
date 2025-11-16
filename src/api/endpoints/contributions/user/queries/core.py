from sqlalchemy import select, RowMapping
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.contributions.shared.contributions import ContributionsCTEContainer
from src.api.endpoints.contributions.user.queries.agreement.agency import get_agency_agreement_cte_container
from src.api.endpoints.contributions.user.queries.agreement.record_type import get_record_type_agreement_cte_container
from src.api.endpoints.contributions.user.queries.agreement.url_type import get_url_type_agreement_cte_container
from src.api.endpoints.contributions.user.queries.annotated_and_validated import AnnotatedAndValidatedCTEContainer
from src.api.endpoints.contributions.user.queries.templates.agreement import AgreementCTEContainer
from src.api.endpoints.contributions.user.response import ContributionsUserResponse, ContributionsUserAgreement
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class GetUserContributionsQueryBuilder(QueryBuilderBase):

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def run(self, session: AsyncSession) -> ContributionsUserResponse:
        inner_cte = AnnotatedAndValidatedCTEContainer(self.user_id)

        contributions_cte = ContributionsCTEContainer()
        record_type_agree: AgreementCTEContainer = get_record_type_agreement_cte_container(inner_cte)
        agency_agree: AgreementCTEContainer = get_agency_agreement_cte_container(inner_cte)
        url_type_agree: AgreementCTEContainer = get_url_type_agreement_cte_container(inner_cte)

        query = (
            select(
                contributions_cte.count,
                record_type_agree.agreement.label("record_type"),
                agency_agree.agreement.label("agency"),
                url_type_agree.agreement.label("url_type")
            )
            .outerjoin(
                record_type_agree.cte,
                contributions_cte.user_id == record_type_agree.user_id
            )
            .outerjoin(
                agency_agree.cte,
                contributions_cte.user_id == agency_agree.user_id
            )
            .outerjoin(
                url_type_agree.cte,
                contributions_cte.user_id == url_type_agree.user_id
            )
            .where(
                contributions_cte.user_id == self.user_id
            )
        )

        try:
            mapping: RowMapping = await sh.mapping(session, query=query)
        except NoResultFound:
            return ContributionsUserResponse(
                count_validated=0,
                agreement=ContributionsUserAgreement(
                    record_type=0,
                    agency=0,
                    url_type=0
                )
            )

        return ContributionsUserResponse(
            count_validated=mapping.count,
            agreement=ContributionsUserAgreement(
                record_type=mapping.record_type or 0,
                agency=mapping.agency or 0,
                url_type=mapping.url_type or 0
            )
        )