from pydantic import BaseModel


class NewURLAgenciesMapping(BaseModel):
    """Denote URLs that need to be added to the database,
    along with the agencies that should be associated with them."""
    url: str
    agency_ids: list[int]