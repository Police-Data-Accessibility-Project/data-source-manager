from enum import Enum


class NameSuggestionSource(Enum):
    HTML_METADATA_TITLE = "HTML Metadata Title"
    USER = "User"