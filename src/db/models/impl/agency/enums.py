from enum import Enum


class AgencyType(Enum):
    UNKNOWN = "unknown"
    INCARCERATION = "incarceration"
    LAW_ENFORCEMENT = "law enforcement"
    COURT = "court"
    AGGREGATED = "aggregated"

class JurisdictionType(Enum):
    SCHOOL = "school"
    COUNTY = "county"
    LOCAL = "local"
    PORT = "port"
    TRIBAL = "tribal"
    TRANSIT = "transit"
    STATE = "state"
    FEDERAL = "federal"