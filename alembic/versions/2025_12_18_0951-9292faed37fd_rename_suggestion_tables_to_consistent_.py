"""Rename suggestion tables to consistent nomenclature

Revision ID: 9292faed37fd
Revises: dfb64594049f
Create Date: 2025-12-18 09:51:20.074946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9292faed37fd'
down_revision: Union[str, None] = 'dfb64594049f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_NEW_TABLE_MAPPING = {
    # Anonymous Suggestions
    "anonymous_annotation_agency": "annotation__anon__agency",
    "anonymous_annotation_location": "annotation__anon__location",
    "anonymous_annotation_record_type": "annotation__anon__record_type",
    "anonymous_annotation_url_type": "annotation__anon__url_type",
    # User Suggestions
    "user_url_agency_suggestions": "annotation__user__agency",
    "user_location_suggestions": "annotation__user__location",
    "user_record_type_suggestions": "annotation__user__record_type",
    "user_url_type_suggestions": "annotation__user__url_type",
    # Auto suggestions
    "auto_location_id_subtasks": "annotation__auto__location__subtasks",
    "location_id_subtask_suggestions": "annotation__auto__location__suggestions",
    "url_auto_agency_id_subtasks": "annotation__auto__agency__subtasks",
    "agency_id_subtask_suggestions": "annotation__auto__agency__suggestions",
    "auto_record_type_suggestions": "annotation__auto__record_type",
    "auto_relevant_suggestions": "annotation__auto__url_type"
}

def upgrade() -> None:
    for old_table_name, new_table_name in OLD_NEW_TABLE_MAPPING.items():
        op.rename_table(
            old_table_name=old_table_name,
            new_table_name=new_table_name
        )


def downgrade() -> None:
    pass
