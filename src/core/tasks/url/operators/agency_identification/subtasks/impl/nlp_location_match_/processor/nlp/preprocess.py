import re

import unicodedata
from bs4 import BeautifulSoup


def preprocess_html(raw_html: str) -> str:
    """Preprocess HTML to extract text content."""
    soup = BeautifulSoup(raw_html, 'lxml')

    # Remove scripts, styles, and other non-textual elements
    for tag in soup(['script','style','noscript','iframe','canvas','svg','header','footer','nav','aside']):
        tag.decompose()
    # Extract text
    text = soup.get_text(separator=' ')
    # Normalize text and collapse whitespace
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[ \t\u00A0]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()