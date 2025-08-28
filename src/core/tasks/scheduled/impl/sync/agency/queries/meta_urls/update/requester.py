from src.db.templates.requester import RequesterBase


class UpdateMetaURLsUpdateURLAndValidationFlagsRequester(RequesterBase):

    async def update_validation_flags(self, url_ids: list[int]) -> None:
        raise NotImplementedError

    async def add_validation_flags(self, url_ids: list[int]) -> None:
        raise NotImplementedError

    async def update_urls(self, url_ids: list[int]) -> None:
        raise NotImplementedError