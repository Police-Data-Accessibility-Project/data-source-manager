from enum import Enum


class URLType(Enum):
    DATA_SOURCE = "data source"
    META_URL = "meta url"
    NOT_RELEVANT = "not relevant"
    INDIVIDUAL_RECORD = "individual record"