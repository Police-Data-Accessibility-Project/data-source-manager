"""Add updated_at triggers

Revision ID: ff4e8b2f6348
Revises: a8f36f185694
Create Date: 2025-10-14 18:37:07.121323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import create_updated_at_trigger

# revision identifiers, used by Alembic.
revision: str = 'ff4e8b2f6348'
down_revision: Union[str, None] = 'a8f36f185694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in [
        "agencies",
        "auto_record_type_suggestions",
        "auto_relevant_suggestions",
        "flag_url_validated",
        "link_batch_urls",
        "link_urls_agency",
        "link_urls_redirect_url",
        "link_urls_root_url",
        "tasks",
        "url_compressed_html",
        "url_internet_archives_probe_metadata",
        "url_scrape_info",
        "url_screenshot",
        "url_web_metadata",
        "urls",
        "user_record_type_suggestions",
        "user_url_type_suggestions",
    ]:
        create_updated_at_trigger(table)


def downgrade() -> None:
    pass
