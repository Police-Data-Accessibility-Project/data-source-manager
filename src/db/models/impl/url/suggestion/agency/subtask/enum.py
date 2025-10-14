from enum import Enum


class AutoAgencyIDSubtaskType(Enum):
    HOMEPAGE_MATCH = "homepage_match"
    NLP_LOCATION_MATCH = "nlp_location_match"
    MUCKROCK = "muckrock_match"
    CKAN = "ckan_match"
    BATCH_LINK = "batch_link"

class SubtaskDetailCode(Enum):
    NO_DETAILS = "no details"
    RETRIEVAL_ERROR = "retrieval error"
    HOMEPAGE_SINGLE_AGENCY = "homepage-single agency"
    HOMEPAGE_MULTI_AGENCY = "homepage-multi agency"