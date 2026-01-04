from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper
from src.util.models.full_url import FullURL


class MockURLRequestInterface:

    def __init__(
        self,
        response_or_responses: URLProbeResponseOuterWrapper | list[URLProbeResponseOuterWrapper]
    ):
        if not isinstance(response_or_responses, list):
            responses = [response_or_responses]
        else:
            responses = response_or_responses

        self._url_to_response = {
            response.original_url.id_form: response for response in responses
        }

    async def probe_urls(self, urls: list[FullURL]) -> list[URLProbeResponseOuterWrapper]:
        return [
            self._url_to_response[url.id_form] for url in urls
        ]
