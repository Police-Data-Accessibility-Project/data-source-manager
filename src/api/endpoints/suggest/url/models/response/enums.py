from enum import Enum


class URLSuggestResultEnum(Enum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_ERRORS = "accepted_with_errors"
    DUPLICATE = "duplicate"
