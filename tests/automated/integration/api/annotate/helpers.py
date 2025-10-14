from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.db.dtos.url.mapping import URLMapping


def check_url_mappings_match(
    map_1: URLMapping,
    map_2: URLMapping
):
    assert map_1.url_id == map_2.url_id
    assert map_2.url == map_2.url


def check_html_info_not_empty(
    html_info: ResponseHTMLInfo
):
    assert not html_info_empty(html_info)


def html_info_empty(
    html_info: ResponseHTMLInfo
) -> bool:
    return html_info.description == "" and html_info.title == ""
