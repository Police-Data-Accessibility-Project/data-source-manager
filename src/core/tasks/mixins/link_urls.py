from abc import abstractmethod

from src.db.client.async_ import AsyncDatabaseClient


class LinkURLsMixin:

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._urls_linked = False
        self._linked_url_ids = []

    @property
    def urls_linked(self) -> bool:
        return self._urls_linked

    @property
    def linked_url_ids(self) -> list[int]:
        return self._linked_url_ids

    @property
    @abstractmethod
    def adb_client(self) -> AsyncDatabaseClient:
        raise NotImplementedError

    @property
    @abstractmethod
    def task_id(self) -> int:
        raise NotImplementedError

    async def link_urls_to_task(self, url_ids: list[int]):
        self._linked_url_ids = url_ids
        if not hasattr(self, "linked_url_ids"):
            raise AttributeError("Class does not have linked_url_ids attribute")
        await self.adb_client.link_urls_to_task(
            task_id=self.task_id,
            url_ids=url_ids
        )
        self._urls_linked = True