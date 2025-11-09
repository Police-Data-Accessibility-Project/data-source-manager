from datetime import datetime

from pydantic import BaseModel


class DSAppLinkInfoModel(BaseModel):
    ds_app_id: int
    updated_at: datetime = datetime.now()