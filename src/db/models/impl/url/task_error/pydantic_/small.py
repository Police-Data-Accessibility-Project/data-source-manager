from pydantic import BaseModel


class URLTaskErrorSmall(BaseModel):
    """Small version of URLTaskErrorPydantic, to be used with the `add_task_errors` method."""
    url_id: int
    error: str