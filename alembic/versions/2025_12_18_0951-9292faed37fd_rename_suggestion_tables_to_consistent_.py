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
    "anonymous_annotation_agency": "annotation__agency__anon",
    "anonymous_annotation_location": "annotation__location__anon",
    "anonymous_annotation_record_type": "annotation__record_type__anon",
    "anonymous_annotation_url_type": "annotation__url_type__anon",
    # User Suggestions
    "user_url_agency_suggestions": "annotation__agency__user",
    "user_location_suggestions": "annotation__location__user",
    "user_record_type_suggestions": "annotation__record_type__user",
    "user_url_type_suggestions": "annotation__url_type__user",
    # Auto suggestions
    "auto_location_id_subtasks": "annotation__location__auto__subtasks",
    "location_id_subtask_suggestions": "annotation__location__auto__suggestions",
    "url_auto_agency_id_subtasks": "annotation__agency__auto__subtasks",
    "agency_id_subtask_suggestions": "annotation__agency__auto__suggestions",
    "auto_record_type_suggestions": "annotation__record_type__auto",
    "auto_relevant_suggestions": "annotation__url_type__auto",
    # Name suggestions
    "url_name_suggestions": "annotation__name__suggestions",
    "link__anonymous_sessions__name_suggestions": "annotation__name__anon__endorsements",
    "link_user_name_suggestions": "annotation__name__user__endorsements",
}

def upgrade() -> None:
    for old_table_name, new_table_name in OLD_NEW_TABLE_MAPPING.items():
        op.rename_table(
            old_table_name=old_table_name,
            new_table_name=new_table_name
        )


def downgrade() -> None:
    pass
