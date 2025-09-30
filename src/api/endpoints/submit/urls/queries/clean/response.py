from pydantic import BaseModel

class CleanURLResponse(BaseModel):
    url_original: str
    url_cleaned: str
