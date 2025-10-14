from pydantic import BaseModel, ConfigDict


class AnnotationPostNameInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_name: str | None = None
    existing_name_id: int | None = None

    @property
    def empty(self) -> bool:
        return self.new_name is None and self.existing_name_id is None