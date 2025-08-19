"""Add internet archives upload task

Revision ID: 8a70ee509a74
Revises: 2a7192657354
Create Date: 2025-08-17 18:30:18.353605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, url_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = '8a70ee509a74'
down_revision: Union[str, None] = '2a7192657354'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

IA_PROBE_METADATA_TABLE_NAME_OLD = "urls_internet_archive_metadata"
IA_PROBE_METADATA_TABLE_NAME_NEW = "url_internet_archives_probe_metadata"

IA_UPLOAD_METADATA_TABLE_NAME = "url_internet_archives_save_metadata"

def upgrade() -> None:
    _create_internet_archive_save_metadata_table()
    op.rename_table(IA_PROBE_METADATA_TABLE_NAME_OLD, IA_PROBE_METADATA_TABLE_NAME_NEW)



def downgrade() -> None:
    op.drop_table(IA_UPLOAD_METADATA_TABLE_NAME)
    op.rename_table(IA_PROBE_METADATA_TABLE_NAME_NEW, IA_PROBE_METADATA_TABLE_NAME_OLD)

def _create_internet_archive_save_metadata_table() -> None:
    op.create_table(
        IA_UPLOAD_METADATA_TABLE_NAME,
        id_column(),
        url_id_column(),
        created_at_column(),
        sa.Column('last_uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )