

TOP_N_LOCATIONS_COUNT: int = 5

INVALID_LOCATION_CHARACTERS: set[str] = {
    "=",
    "\\",
    "/",
    "\'",
    "\","
}

# State ISOs that commonly align with other words,
# Which cannot be used in simple text scanning
INVALID_SCAN_ISOS: set[str] = {
    "IN",
    "OR",
    "ME",
    "ID"
}

BLACKLISTED_WORDS: set[str] = {
    "the united states",
    "download",
    "geoplatform"
}