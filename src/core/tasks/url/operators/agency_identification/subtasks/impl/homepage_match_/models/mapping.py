from pydantic import BaseModel


class SubtaskURLMapping(BaseModel):
    url_id: int
    subtask_id: int