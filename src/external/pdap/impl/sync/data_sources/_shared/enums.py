from enum import Enum


class DetailLevel(Enum):
    """
    Correlates to the detail_level enum in the database
    """

    INDIVIDUAL = "Individual record"
    AGGREGATED = "Aggregated records"
    SUMMARIZED = "Summarized totals"
