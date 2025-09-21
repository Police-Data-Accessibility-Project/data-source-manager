from enum import Enum


# TODO (SM422): Rename to URLType
class URLValidatedType(Enum):
    DATA_SOURCE = "data source"
    META_URL = "meta url"
    NOT_RELEVANT = "not relevant"
    INDIVIDUAL_RECORD = "individual record"