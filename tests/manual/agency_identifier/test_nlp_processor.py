import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.core import \
    NLPProcessor

SAMPLE_HTML: str = """
<html>
I live in Pittsburgh, Allegheny, Pennsylvania.
</html>
"""

@pytest.mark.asyncio
async def test_nlp_processor_happy_path():
    nlp_processor = NLPProcessor()
    response = nlp_processor.parse_for_locations(SAMPLE_HTML)
    print(response)

@pytest.mark.asyncio
async def test_nlp_processor_empty_html():
    nlp_processor = NLPProcessor()
    response = nlp_processor.parse_for_locations("<html></html>")
    print(response)