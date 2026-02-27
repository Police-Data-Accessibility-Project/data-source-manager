"""Materialize url_annotation_count_view and url_annotation_flags

Revision ID: c8e4f1a2b3d5
Revises: 759ce7d0772b
Create Date: 2026-02-26 00:00:00.000000

"""
from typing import Optional, Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c8e4f1a2b3d5'
down_revision: Optional[str] = '759ce7d0772b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_URL_ANNOTATION_COUNT_VIEW_SQL = """
            WITH
    auto_location_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__location__auto__subtasks anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , auto_agency_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__agency__auto__subtasks anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , auto_url_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__url_type__auto anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , auto_record_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__record_type__auto anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , user_location_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__location__user anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , user_agency_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__agency__user anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , user_url_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__url_type__user anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , user_record_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__record_type__user anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , anon_location_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__location__anon anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , anon_agency_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__agency__anon anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , anon_url_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__url_type__anon anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
    , anon_record_type_count AS (
        SELECT
            u_1.id,
            count(anno.url_id) AS cnt
        FROM
            urls u_1
            JOIN annotation__record_type__anon anno
                 ON u_1.id = anno.url_id
        GROUP BY
            u_1.id
        )
SELECT
    u.id AS url_id,
    COALESCE(auto_ag.cnt, 0::bigint) AS auto_agency_count,
    COALESCE(auto_loc.cnt, 0::bigint) AS auto_location_count,
    COALESCE(auto_rec.cnt, 0::bigint) AS auto_record_type_count,
    COALESCE(auto_typ.cnt, 0::bigint) AS auto_url_type_count,
    COALESCE(user_ag.cnt, 0::bigint) AS user_agency_count,
    COALESCE(user_loc.cnt, 0::bigint) AS user_location_count,
    COALESCE(user_rec.cnt, 0::bigint) AS user_record_type_count,
    COALESCE(user_typ.cnt, 0::bigint) AS user_url_type_count,
    COALESCE(anon_ag.cnt, 0::bigint) AS anon_agency_count,
    COALESCE(anon_loc.cnt, 0::bigint) AS anon_location_count,
    COALESCE(anon_rec.cnt, 0::bigint) AS anon_record_type_count,
    COALESCE(anon_typ.cnt, 0::bigint) AS anon_url_type_count,
    COALESCE(auto_ag.cnt, 0::bigint) + COALESCE(auto_loc.cnt, 0::bigint) + COALESCE(auto_rec.cnt, 0::bigint) +
    COALESCE(auto_typ.cnt, 0::bigint) + COALESCE(user_ag.cnt, 0::bigint) + COALESCE(user_loc.cnt, 0::bigint) +
    COALESCE(user_rec.cnt, 0::bigint) + COALESCE(user_typ.cnt, 0::bigint) + COALESCE(anon_ag.cnt, 0::bigint) +
    COALESCE(anon_loc.cnt, 0::bigint) + COALESCE(anon_rec.cnt, 0::bigint) + COALESCE(anon_typ.cnt, 0::bigint) AS total_anno_count

FROM
    urls u
    LEFT JOIN auto_agency_count auto_ag
              ON auto_ag.id = u.id
    LEFT JOIN auto_location_count auto_loc
              ON auto_loc.id = u.id
    LEFT JOIN auto_record_type_count auto_rec
              ON auto_rec.id = u.id
    LEFT JOIN auto_url_type_count auto_typ
              ON auto_typ.id = u.id
    LEFT JOIN user_agency_count user_ag
              ON user_ag.id = u.id
    LEFT JOIN user_location_count user_loc
              ON user_loc.id = u.id
    LEFT JOIN user_record_type_count user_rec
              ON user_rec.id = u.id
    LEFT JOIN user_url_type_count user_typ
              ON user_typ.id = u.id
    LEFT JOIN anon_agency_count anon_ag
              ON anon_ag.id = u.id
    LEFT JOIN anon_location_count anon_loc
              ON anon_loc.id = u.id
    LEFT JOIN anon_record_type_count anon_rec
              ON anon_rec.id = u.id
    LEFT JOIN anon_url_type_count anon_typ
              ON anon_typ.id = u.id
"""

_URL_ANNOTATION_FLAGS_SQL = """
SELECT u.id as url_id,
        EXISTS (SELECT 1 FROM public.annotation__record_type__auto    a WHERE a.url_id = u.id) AS has_auto_record_type_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__url_type__auto       a WHERE a.url_id = u.id) AS has_auto_relevant_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__agency__auto__subtasks a WHERE a.url_id = u.id) AS has_auto_agency_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__location__auto__subtasks a WHERE a.url_id = u.id) AS has_auto_location_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__record_type__user    a WHERE a.url_id = u.id) AS has_user_record_type_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__url_type__user       a WHERE a.url_id = u.id) AS has_user_relevant_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__agency__user         a WHERE a.url_id = u.id) AS has_user_agency_suggestion,
        EXISTS (SELECT 1 FROM public.annotation__location__user       a WHERE a.url_id = u.id) AS has_user_location_suggestion,
        EXISTS (SELECT 1 FROM public.link_agencies__urls              a WHERE a.url_id = u.id) AS has_confirmed_agency,
        EXISTS (SELECT 1 FROM public.reviewing_user_url               a WHERE a.url_id = u.id) AS was_reviewed
FROM urls u
"""


def upgrade() -> None:
    """Convert url_annotation_count_view and url_annotation_flags to materialized views."""
    # Drop regular views
    op.execute("DROP VIEW IF EXISTS url_annotation_count_view")
    op.execute("DROP VIEW IF EXISTS url_annotation_flags")

    # Recreate as materialized views
    op.execute(
        f"CREATE MATERIALIZED VIEW url_annotation_count_view AS {_URL_ANNOTATION_COUNT_VIEW_SQL}"
    )
    op.execute(
        f"CREATE MATERIALIZED VIEW url_annotation_flags AS {_URL_ANNOTATION_FLAGS_SQL}"
    )

    # Unique indexes required for REFRESH MATERIALIZED VIEW CONCURRENTLY
    op.execute("CREATE UNIQUE INDEX ON url_annotation_count_view (url_id)")
    op.execute("CREATE UNIQUE INDEX ON url_annotation_flags (url_id)")


def downgrade() -> None:
    """Revert url_annotation_count_view and url_annotation_flags to regular views."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS url_annotation_count_view")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS url_annotation_flags")

    # Recreate as regular views
    op.execute(
        f"CREATE VIEW url_annotation_count_view AS {_URL_ANNOTATION_COUNT_VIEW_SQL}"
    )
    op.execute(
        f"CREATE OR REPLACE VIEW url_annotation_flags AS ({_URL_ANNOTATION_FLAGS_SQL})"
    )
