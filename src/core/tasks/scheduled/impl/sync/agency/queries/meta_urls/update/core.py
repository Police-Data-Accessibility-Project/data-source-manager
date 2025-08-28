from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.update.filter import \
    filter_urls_with_non_meta_record_type, filter_urls_with_non_meta_url_validation_flag, \
    filter_urls_without_validation_flag
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.update.params import UpdateMetaURLsParams
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.update.requester import UpdateMetaURLsRequester, \
    UpdateMetaURLsUpdateURLAndValidationFlagsRequester
from src.db.queries.base.builder import QueryBuilderBase


class UpdateMetaURLsQueryBuilder(QueryBuilderBase):
    """Update meta URLs in DB

    Meta URLs should be given a validation status as a Meta URL
    and have their record type updated to CONTACT_INFO_AND_AGENCY_META
    """

    def __init__(
        self,
        params: list[UpdateMetaURLsParams]
    ):
        super().__init__()
        self.params = params

    async def run(
        self,
        session: AsyncSession
    ) -> None:
        requester = UpdateMetaURLsUpdateURLAndValidationFlagsRequester(session)

        urls_with_non_meta_record_type: list[int] = filter_urls_with_non_meta_record_type(self.params)
        await requester.update_urls(urls_with_non_meta_record_type)

        urls_without_validation_flag: list[int] = filter_urls_without_validation_flag(self.params)
        await requester.add_validation_flags(urls_without_validation_flag)

        urls_with_non_meta_url_validation_flag: list[int] = filter_urls_with_non_meta_url_validation_flag(self.params)
        await requester.update_validation_flags(urls_with_non_meta_url_validation_flag)





        raise NotImplementedError
