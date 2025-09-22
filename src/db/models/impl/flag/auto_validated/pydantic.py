from pydantic import BaseModel

from src.db.models.impl.flag.auto_validated.sqlalchemy import FlagURLAutoValidated


class FlagURLAutoValidatedPydantic(BaseModel):

    url_id: int

    @classmethod
    def sa_model(cls) -> type[FlagURLAutoValidated]:
        return FlagURLAutoValidated