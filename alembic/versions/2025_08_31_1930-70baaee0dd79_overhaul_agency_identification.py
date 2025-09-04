"""Overhaul agency identification

Revision ID: 70baaee0dd79
Revises: b741b65a1431
Create Date: 2025-08-31 19:30:20.690369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, url_id_column, created_at_column, agency_id_column, updated_at_column, \
    task_id_column

# revision identifiers, used by Alembic.
revision: str = '70baaee0dd79'
down_revision: Union[str, None] = 'b741b65a1431'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

URL_HAS_AGENCY_SUGGESTIONS_VIEW_NAME: str = "url_has_agency_auto_suggestions_view"
URL_UNKNOWN_AGENCIES_VIEW_NAME: str = "url_unknown_agencies_view"

URL_AUTO_AGENCY_SUBTASK_TABLE_NAME: str = "url_auto_agency_id_subtasks"
LINK_AGENCY_ID_SUBTASK_AGENCIES_TABLE_NAME: str = "agency_id_subtask_suggestions"

URL_AUTO_AGENCY_SUGGESTIONS_TABLE_NAME: str = "url_auto_agency_suggestions"

AGENCY_AUTO_SUGGESTION_METHOD_ENUM = sa.dialects.postgresql.ENUM(
    name="agency_auto_suggestion_method",
    create_type=False
)

SUBTASK_DETAIL_CODE_ENUM = sa.Enum(
    'no details',
    'retrieval error',
    'case-homepage-single agency',
    'case-homepage-no data sources',
    'case-homepage-multi agency nonzero data sources',
    name="agency_id_subtask_detail_code",
)


def upgrade() -> None:
    _create_url_auto_agency_subtask_table()
    _create_url_unknown_agencies_view()
    _create_link_agency_id_subtask_agencies_table()
    _create_url_has_agency_suggestions_view()
    _create_new_url_annotation_flags_view()
    _drop_url_auto_agency_suggestions_table()


def downgrade() -> None:
    _drop_url_unknown_agencies_view()
    _create_url_auto_agency_suggestions_table()
    _create_old_url_annotation_flags_view()
    _drop_url_has_agency_suggestions_view()
    _drop_link_agency_id_subtask_agencies_table()
    _drop_url_auto_agency_subtask_table()
    SUBTASK_DETAIL_CODE_ENUM.drop(op.get_bind())


def _drop_url_auto_agency_suggestions_table():
    op.drop_table(URL_AUTO_AGENCY_SUGGESTIONS_TABLE_NAME)


def _create_new_url_annotation_flags_view():
    op.execute(
        f"""
        CREATE OR REPLACE VIEW url_annotation_flags AS
        (
        SELECT u.id,
               CASE WHEN arts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_record_type_suggestion,
               CASE WHEN ars.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_auto_relevant_suggestion,
               auas.has_agency_suggestions AS has_auto_agency_suggestion,
               CASE WHEN urts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_record_type_suggestion,
               CASE WHEN urs.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_user_relevant_suggestion,
               CASE WHEN uuas.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_agency_suggestion,
               CASE WHEN lua.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_confirmed_agency,
               CASE WHEN ruu.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS was_reviewed
        FROM urls u
                 LEFT JOIN public.auto_record_type_suggestions arts ON u.id = arts.url_id
                 LEFT JOIN public.auto_relevant_suggestions ars ON u.id = ars.url_id
                 LEFT JOIN public.{URL_HAS_AGENCY_SUGGESTIONS_VIEW_NAME} auas ON u.id = auas.url_id
                 LEFT JOIN public.user_record_type_suggestions urts ON u.id = urts.url_id
                 LEFT JOIN public.user_relevant_suggestions urs ON u.id = urs.url_id
                 LEFT JOIN public.user_url_agency_suggestions uuas ON u.id = uuas.url_id
                 LEFT JOIN public.reviewing_user_url ruu ON u.id = ruu.url_id
                 LEFT JOIN public.link_urls_agency lua on u.id = lua.url_id
            )
        """
    )


def _create_url_has_agency_suggestions_view():
    op.execute(
        f"""
    CREATE OR REPLACE VIEW {URL_HAS_AGENCY_SUGGESTIONS_VIEW_NAME} AS
    SELECT 
        u.id as url_id,
        (uas.id IS NOT NULL) AS has_agency_suggestions
    FROM public.urls u
    LEFT JOIN public.{URL_AUTO_AGENCY_SUBTASK_TABLE_NAME} uas on u.id = uas.url_id
    """
        )
    pass


def _create_url_unknown_agencies_view():
    op.execute(
        f"""
    CREATE OR REPLACE VIEW {URL_UNKNOWN_AGENCIES_VIEW_NAME} AS
    SELECT 
        u.id
    FROM urls u
    LEFT JOIN {URL_AUTO_AGENCY_SUBTASK_TABLE_NAME} uas ON u.id = uas.url_id
    GROUP BY u.id
    HAVING bool_or(uas.agencies_found) = false
    """
        )


def _create_url_auto_agency_subtask_table():
    op.create_table(
        URL_AUTO_AGENCY_SUBTASK_TABLE_NAME,
        id_column(),
        task_id_column(),
        url_id_column(),
        sa.Column(
            "subtask",
            AGENCY_AUTO_SUGGESTION_METHOD_ENUM,
            nullable=False
        ),
        sa.Column(
            "agencies_found",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "detail",
            SUBTASK_DETAIL_CODE_ENUM,
            server_default=sa.text("'no details'"),
            nullable=False
        ),
        created_at_column()
    )


def _create_link_agency_id_subtask_agencies_table():
    op.create_table(
        LINK_AGENCY_ID_SUBTASK_AGENCIES_TABLE_NAME,
        sa.Column(
            "subtask_id",
            sa.Integer(),
            sa.ForeignKey(
                f'{URL_AUTO_AGENCY_SUBTASK_TABLE_NAME}.id',
                ondelete='CASCADE'
            ),
            nullable=False,
            comment='A foreign key to the `url_auto_agency_subtask` table.'
        ),
        sa.Column(
            "confidence",
            sa.Integer,
            sa.CheckConstraint(
                "confidence BETWEEN 0 and 100"
            ),
            nullable=False,
        ),
        agency_id_column(),
        created_at_column()
    )


def _drop_link_agency_id_subtask_agencies_table():
    op.drop_table(LINK_AGENCY_ID_SUBTASK_AGENCIES_TABLE_NAME)


def _drop_url_auto_agency_subtask_table():
    op.drop_table(URL_AUTO_AGENCY_SUBTASK_TABLE_NAME)


def _create_url_auto_agency_suggestions_table():
    op.create_table(
        URL_AUTO_AGENCY_SUGGESTIONS_TABLE_NAME,
        id_column(),
        agency_id_column(),
        url_id_column(),
        sa.Column(
            "is_unknown",
            sa.Boolean(),
            nullable=False
        ),
        created_at_column(),
        updated_at_column(),
        sa.Column(
            'method',
            AGENCY_AUTO_SUGGESTION_METHOD_ENUM,
            nullable=True
        ),
        sa.Column(
            'confidence',
            sa.Float(),
            server_default=sa.text('0.0'),
            nullable=False
        ),
        sa.UniqueConstraint("agency_id", "url_id")
    )


def _drop_url_unknown_agencies_view():
    op.execute(f"DROP VIEW IF EXISTS {URL_UNKNOWN_AGENCIES_VIEW_NAME}")


def _drop_url_has_agency_suggestions_view():
    op.execute(f"DROP VIEW IF EXISTS {URL_HAS_AGENCY_SUGGESTIONS_VIEW_NAME}")


def _drop_url_annotation_flags_view():
    op.execute("DROP VIEW url_annotation_flags;")


def _create_old_url_annotation_flags_view():
    op.execute(
        f"""
        CREATE OR REPLACE VIEW url_annotation_flags AS
        (
        SELECT u.id,
               CASE WHEN arts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_record_type_suggestion,
               CASE WHEN ars.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_auto_relevant_suggestion,
               CASE WHEN auas.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_agency_suggestion,
               CASE WHEN urts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_record_type_suggestion,
               CASE WHEN urs.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_user_relevant_suggestion,
               CASE WHEN uuas.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_agency_suggestion,
               CASE WHEN cua.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS has_confirmed_agency,
               CASE WHEN ruu.url_id IS NOT NULL THEN TRUE ELSE FALSE END  AS was_reviewed
        FROM urls u
                 LEFT JOIN public.auto_record_type_suggestions arts ON u.id = arts.url_id
                 LEFT JOIN public.auto_relevant_suggestions ars ON u.id = ars.url_id
                 LEFT JOIN public.{URL_AUTO_AGENCY_SUGGESTIONS_TABLE_NAME} auas ON u.id = auas.url_id
                 LEFT JOIN public.user_record_type_suggestions urts ON u.id = urts.url_id
                 LEFT JOIN public.user_relevant_suggestions urs ON u.id = urs.url_id
                 LEFT JOIN public.user_url_agency_suggestions uuas ON u.id = uuas.url_id
                 LEFT JOIN public.reviewing_user_url ruu ON u.id = ruu.url_id
                 LEFT JOIN public.link_urls_agency cua on u.id = cua.url_id
            )
               """
    )
