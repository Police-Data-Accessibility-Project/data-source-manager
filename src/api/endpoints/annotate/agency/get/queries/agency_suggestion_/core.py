from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.agency.get.queries.agency_suggestion_.suggestions_with_highest_confidence import \
    SuggestionsWithHighestConfidenceCTE
from src.core.enums import SuggestionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetAgencySuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> list[GetNextURLForAgencyAgencyInfo]:
        # Get relevant autosuggestions and agency info, if an associated agency exists

        cte = SuggestionsWithHighestConfidenceCTE()

        query = (
            select(
                cte.agency_id,
                cte.confidence,
                Agency.name,
                Agency.state,
                Agency.county,
                Agency.locality
            )
            .outerjoin(
                Agency,
                Agency.agency_id == cte.agency_id
            )
            .where(
                cte.url_id == self.url_id
            )
        )

        raw_autosuggestions: Sequence[RowMapping] = await sh.mappings(session, query=query)
        if len(raw_autosuggestions) == 0:
            # Unknown agency
            return [
                GetNextURLForAgencyAgencyInfo(
                    suggestion_type=SuggestionType.UNKNOWN,
                )
            ]

        agency_suggestions: list[GetNextURLForAgencyAgencyInfo] = []
        for autosuggestion in raw_autosuggestions:
            agency_id: int = autosuggestion["agency_id"]
            name: str = autosuggestion["name"]
            state: str | None = autosuggestion["state"]
            county: str | None = autosuggestion["county"]
            locality: str | None = autosuggestion["locality"]
            agency_suggestions.append(
                GetNextURLForAgencyAgencyInfo(
                    suggestion_type=SuggestionType.AUTO_SUGGESTION,
                    pdap_agency_id=agency_id,
                    agency_name=name,
                    state=state,
                    county=county,
                    locality=locality
                )
            )
        return agency_suggestions