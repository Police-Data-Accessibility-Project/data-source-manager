from urllib.parse import urlparse

from src.util.url import clean_url


class FullURL:
    __slots__ = (
        "_full_url",
        "_scheme",
        "_url_without_scheme"
    )

    def __init__(
        self,
        full_url: str
    ):
        if not isinstance(full_url, str):
            raise ValueError("full_url must be a string")
        self._full_url = full_url
        self._scheme = None
        self._url_without_scheme = None

    @property
    def full_url(self) -> str:
        return self._full_url

    def __str__(self):
        return self.full_url

    def __repr__(self):
        return self.id_form

    def __hash__(self):
        return hash(self.id_form)

    def __eq__(self, other):
        return isinstance(other, FullURL) and self.id_form == other.id_form

    def _set_url_parts(self):
        """
        Modifies:
            self._scheme
            self._url

        """
        parse_result = urlparse(self.full_url)
        self._scheme = parse_result.scheme
        if parse_result.scheme is not None:
            self._url_without_scheme = self.full_url.replace(f"{parse_result.scheme}://", "", 1)
        else:
            self._url_without_scheme = self.full_url


    @property
    def scheme(self) -> str | None:
        if self._scheme is None:
            self._set_url_parts()
        return self._scheme

    @property
    def without_scheme(self) -> str:
        if self._url_without_scheme is None:
            self._set_url_parts()
        return self._url_without_scheme

    @property
    def id_form(self) -> str:
        """Retrieves URL in 'Identification Form'

        These are meant to be used to compare URLs with one another.

        They have the following properties:
            No Scheme
            No Trailing Slash
            Cleaned of fragments and query parameters.
        """
        no_scheme: str = self.without_scheme
        no_trailing_slash: str = no_scheme.rstrip("/")
        clean: str = clean_url(no_trailing_slash)
        return clean

    def clean(self) -> str:
        return clean_url(self.full_url)

