"""Add location annotation logic

Revision ID: 93cbaa3b8e9b
Revises: d5f92e6fedf4
Create Date: 2025-09-15 19:05:27.872875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type, url_id_column, location_id_column, created_at_column, id_column, \
    task_id_column, agency_id_column

# revision identifiers, used by Alembic.
revision: str = '93cbaa3b8e9b'
down_revision: Union[str, None] = 'd5f92e6fedf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_LOCATION_SUGGESTIONS_TABLE_NAME = 'user_location_suggestions'
AUTO_LOCATION_ID_SUBTASK_TABLE_NAME = 'auto_location_id_subtask'
LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME = 'location_id_subtask_suggestions'
LOCATION_ID_TASK_TYPE = 'location_id'
LOCATION_ID_SUBTASK_TYPE_NAME = 'location_id_subtask_type'

def upgrade() -> None:
    _add_location_id_task_type()
    _create_user_location_suggestions_table()
    _create_auto_location_id_subtask_table()
    _create_location_id_subtask_suggestions_table()

def downgrade() -> None:
    _drop_location_id_subtask_suggestions_table()
    _drop_auto_location_id_subtask_table()
    _drop_user_location_suggestions_table()
    _drop_location_id_task_type()
    _drop_location_id_subtask_type()

def _add_location_id_task_type():
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
            'Screenshot',
            LOCATION_ID_TASK_TYPE
        ]
    )


def _create_user_location_suggestions_table():
    op.create_table(
        USER_LOCATION_SUGGESTIONS_TABLE_NAME,
        url_id_column(),
        location_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'url_id',
            'location_id',
            name='user_location_suggestions_url_id_location_id_pk'
        )
    )


def _create_auto_location_id_subtask_table():
    op.create_table(
        AUTO_LOCATION_ID_SUBTASK_TABLE_NAME,
        id_column(),
        task_id_column(),
        url_id_column(),
        sa.Column(
            'locations_found',
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            'type',
            sa.Enum(
                'nlp_location_frequency',
                name='auto_location_id_subtask_type'
            ),
            nullable=False
        ),
        created_at_column(),
        sa.UniqueConstraint(
            'url_id',
            'type',
            name='auto_location_id_subtask_url_id_type_unique'
        )
    )


def _create_location_id_subtask_suggestions_table():
    op.create_table(
        LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME,
        sa.Column(
            'subtask_id',
            sa.Integer(),
            sa.ForeignKey(
                'auto_location_id_subtask.id',
                ondelete='CASCADE'
            ),
            primary_key=True
        ),
        location_id_column(),
        sa.Column(
            'confidence',
            sa.Float(),
            nullable=False
        ),
        created_at_column(),
    )



def _drop_location_id_task_type():
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
            'Screenshot',
        ]
    )


def _drop_auto_location_id_subtask_table():
    op.drop_table(AUTO_LOCATION_ID_SUBTASK_TABLE_NAME)


def _drop_user_location_suggestions_table():
    op.drop_table(USER_LOCATION_SUGGESTIONS_TABLE_NAME)


def _drop_location_id_subtask_suggestions_table():
    op.drop_table(LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME)

def _drop_location_id_subtask_type():
    op.execute("""
    DROP TYPE IF EXISTS auto_location_id_subtask_type;
    """)

