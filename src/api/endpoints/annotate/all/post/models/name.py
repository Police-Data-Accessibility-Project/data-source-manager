from pydantic import BaseModel


class AnnotationPostNameInfo(BaseModel):
    new_name: str | None = None
    existing_name_id: int | None = None

    @property
    def empty(self) -> bool:
        return self.new_name is None and self.existing_name_id is None