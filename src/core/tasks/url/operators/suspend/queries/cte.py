from sqlalchemy import select, func, Select, exists, or_

from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.views.unvalidated_url import UnvalidatedURL


class GetURLsForSuspensionCTEContainer:

    def __init__(self):
        self.cte = (
            select(
                UnvalidatedURL.url_id
            )
            .outerjoin(
                LinkUserSuggestionAgencyNotFound,
                UnvalidatedURL.url_id == LinkUserSuggestionAgencyNotFound.url_id
            )
            .outerjoin(
                LinkUserSuggestionLocationNotFound,
                UnvalidatedURL.url_id == LinkUserSuggestionLocationNotFound.url_id
            )
            .where(
                ~exists(
                    select(
                        FlagURLSuspended.url_id
                    )
                    .where(
                        FlagURLSuspended.url_id == UnvalidatedURL.url_id
                    )
                )
            )
            .group_by(
                UnvalidatedURL.url_id
            )
            .having(
                or_(
                    func.count(LinkUserSuggestionAgencyNotFound.user_id) >= 2,
                    func.count(LinkUserSuggestionLocationNotFound.user_id) >= 2,
                )
            )
            .cte("get_urls_for_suspension")
        )

    @property
    def query(self) -> Select:
        return select(self.cte.c.url_id)