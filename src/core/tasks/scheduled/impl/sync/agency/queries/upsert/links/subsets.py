from pydantic import BaseModel


class AgencyMetaURLLinkSubsets(BaseModel):
    agency_id: int
    add: list[int]
    remove: list[int]
    do_nothing: list[int]