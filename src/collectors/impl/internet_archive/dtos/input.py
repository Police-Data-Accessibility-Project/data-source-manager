from pydantic import BaseModel, Field


DEFAULT_EXCLUDE_PATTERNS = [
    r"/wp-content/", r"/wp-includes/", r"/wp-json/", r"/feed/",
    r"utm_", r"fbclid", r"xmlrpc\.php",
]


class InternetArchiveInputDTO(BaseModel):
    urls: list[str] = Field(
        description="Seed URLs to extract domains from",
        min_length=1,
        max_length=50,
    )
    max_results_per_domain: int = Field(
        description="Maximum number of results per domain",
        default=10000,
        ge=100,
        le=50000,
    )
    exclude_patterns: list[str] = Field(
        description="Regex patterns for URLs to exclude",
        default=DEFAULT_EXCLUDE_PATTERNS,
    )
    mime_type_allowlist: list[str] = Field(
        description="Allowed MIME types",
        default=["text/html"],
    )
