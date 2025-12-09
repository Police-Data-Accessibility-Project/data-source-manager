from enum import Enum


class AgencyAggregationEnum(Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    LOCALITY = "local"

class UpdateMethodEnum(Enum):
    OVERWRITE = "Overwrite"
    INSERT = "Insert"
    NO_UPDATES = "No updates"

class RetentionScheduleEnum(Enum):
    FUTURE_ONLY = "Future only"
    ONE_MONTH = "1 month"
    ONE_DAY = "1 day"
    ONE_WEEK = "1 week"
    ONE_TO_TEN_YEARS = "1-10 years"
    LT_1_DAY = "< 1 day"
    LT_1_WEEK = "< 1 week"
    LT_1_YEAR = "< 1 year"
    GT_10_YEARS = "> 10 years"

class AccessTypeEnum(Enum):
    WEBPAGE = "Webpage"
    DOWNLOAD = "Download"
    API = "API"