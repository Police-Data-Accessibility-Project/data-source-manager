"""Revise annotation count view

Revision ID: 42933d84aa52
Revises: e88e4e962dc7
Create Date: 2025-12-26 15:27:30.368862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42933d84aa52'
down_revision: Union[str, None] = 'e88e4e962dc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""DROP VIEW IF EXISTS url_annotation_count_view""")
    op.execute(
        """
        CREATE VIEW url_annotation_count_view AS
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
                      ON user_ag.id = u.id
            LEFT JOIN anon_location_count anon_loc
                      ON user_loc.id = u.id
            LEFT JOIN anon_record_type_count anon_rec
                      ON user_rec.id = u.id
            LEFT JOIN anon_url_type_count anon_typ
                      ON user_typ.id = u.id

        """
    )


def downgrade() -> None:
    pass
