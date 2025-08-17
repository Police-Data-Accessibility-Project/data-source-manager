from abc import ABC, abstractmethod


class HasPrerequisitesMixin(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    async def meets_task_prerequisites(self) -> bool:
        """
        A task should not be initiated unless certain
        conditions are met
        """
        raise NotImplementedError