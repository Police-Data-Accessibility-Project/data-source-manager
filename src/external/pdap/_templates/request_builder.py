from abc import ABC, abstractmethod

from pdap_access_manager import AccessManager

class PDAPClientRequestBuilderBase(ABC):

    @abstractmethod
    async def run(self, access_manager: AccessManager):
        raise NotImplementedError