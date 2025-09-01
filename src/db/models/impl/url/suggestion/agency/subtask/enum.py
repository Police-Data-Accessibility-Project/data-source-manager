from enum import Enum


class AutoAgencyIDSubtask(Enum):
    HOMEPAGE_MATCH = "homepage_match"
    NLP_LOCATION_MATCH = "nlp_location_match"
    MUCKROCK = "muckrock_match"
    CKAN = "ckan_match"

class SubtaskDetailCode(Enum):
    NO_DETAILS = "no details"
    BLACKLIST_CKAN_NO_CKAN_COLLECTOR = "blacklist-ckan-no ckan collector"
    BLACKLIST_MUCKROCK_NO_MUCKROCK_COLLECTOR = "blacklist-muckrock-no muckrock collector"
    BLACKLIST_NLP_NO_HTML = "blacklist-nlp-no html"
    BLACKLIST_HOMEPAGE_ROOT_URL = "blacklist-homepage-root url"
    BLACKLIST_HOMEPAGE_NO_META_URLS_ASSOCIATED_WITH_ROOT = "blacklist-homepage-no meta urls associated with root"
    CASE_HOMEPAGE_SINGLE_AGENCY = "case-homepage-single agency"
    CASE_HOMEPAGE_NO_DATA_SOURCES = "case-homepage-no data sources"
    CASE_HOMEPAGE_MULTI_AGENCY_NONZERO_DATA_SOURCES = "case-homepage-multi agency nonzero data sources"