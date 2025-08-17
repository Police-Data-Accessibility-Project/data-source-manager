from enum import Enum


class IntervalEnum(Enum):
    DAILY = 60 * 24
    HOURLY = 60
    TEN_MINUTES = 10