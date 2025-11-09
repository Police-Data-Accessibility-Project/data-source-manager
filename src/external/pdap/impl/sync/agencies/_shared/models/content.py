class AgencySyncContentModel(BaseModel):
    # Required
    name: str
    jurisdiction_type: JurisdictionType
    agency_type: AgencyType
    location_ids: list[int] = Field(min_length=1)

    # Optional
    no_web_presence: bool = False
    defunct_year: int | None = None
