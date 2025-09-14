"""Create url screenshot task 

Revision ID: e7189dc92a83
Revises: 70baaee0dd79
Create Date: 2025-09-12 20:40:45.950204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type, id_column, url_id_column, created_at_column, updated_at_column

# revision identifiers, used by Alembic.
revision: str = 'e7189dc92a83'
down_revision: Union[str, None] = '70baaee0dd79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

URL_SCREENSHOT_TABLE_NAME = "url_screenshot"
SCREENSHOT_ERROR_TABLE_NAME = "error_url_screenshot"



def upgrade() -> None:
    _add_url_screenshot_task()
    _add_url_screenshot_table()
    _add_screenshot_error_table()



def downgrade() -> None:
    _remove_url_screenshot_task()
    _remove_url_screenshot_table()
    _remove_screenshot_error_table()


def _add_screenshot_error_table():
    op.create_table(
        SCREENSHOT_ERROR_TABLE_NAME,
        url_id_column(),
        sa.Column('error', sa.String(), nullable=False),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id')
    )


def _add_url_screenshot_table():
    op.create_table(
        URL_SCREENSHOT_TABLE_NAME,
        url_id_column(),
        sa.Column('content', sa.LargeBinary(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', name='uq_url_id_url_screenshot')
    )


def _remove_url_screenshot_table():
    op.drop_table(URL_SCREENSHOT_TABLE_NAME)


def _remove_screenshot_error_table():
    op.drop_table(SCREENSHOT_ERROR_TABLE_NAME)


def _add_url_screenshot_task():
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources',
            'Push to Hugging Face',
            'URL Probe',
            'Populate Backlog Snapshot',
            'Delete Old Logs',
            'Run URL Task Cycles',
            'Root URL',
            'Internet Archives Probe',
            'Internet Archives Archive',
            'Screenshot'
        ]
    )

def _remove_url_screenshot_task():
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources',
            'Push to Hugging Face',
            'URL Probe',
            'Populate Backlog Snapshot',
            'Delete Old Logs',
            'Run URL Task Cycles',
            'Root URL',
            'Internet Archives Probe',
            'Internet Archives Archive'
        ]
    )