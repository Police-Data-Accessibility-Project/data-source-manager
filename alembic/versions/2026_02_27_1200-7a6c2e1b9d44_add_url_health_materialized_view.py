"""Add url health view

Revision ID: 7a6c2e1b9d44
Revises: 1fb2286a016c
Create Date: 2026-02-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7a6c2e1b9d44"
down_revision: Union[str, None] = "1fb2286a016c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_url_health_view() -> None:
    op.execute(
        """
        CREATE VIEW url_health_view AS
        WITH latest_redirect AS (
            SELECT DISTINCT ON (lur.source_url_id)
                lur.source_url_id,
                lur.destination_url_id
            FROM link_urls_redirect_url lur
            ORDER BY lur.source_url_id, lur.updated_at DESC, lur.created_at DESC
        )
        SELECT
            u.id AS url_id,
            CASE
                WHEN uwm.status_code = 200 THEN 'OK'
                WHEN lr.destination_url_id IS NOT NULL AND redirect_uwm.status_code = 200 THEN 'OK'
                WHEN uiapm.archive_url IS NOT NULL THEN 'Archived'
                ELSE 'Broken'
            END AS health,
            CASE
                WHEN uwm.status_code = 200 THEN 100
                WHEN lr.destination_url_id IS NOT NULL AND redirect_uwm.status_code = 200 THEN 150
                WHEN uiapm.archive_url IS NOT NULL THEN 200
                ELSE 300
            END AS code,
            uwm.status_code,
            lr.destination_url_id AS redirect_url_id,
            CASE
                WHEN redirect_u.scheme IS NOT NULL AND redirect_u.trailing_slash = TRUE
                    THEN redirect_u.scheme || '://' || redirect_u.url || '/'
                WHEN redirect_u.scheme IS NOT NULL AND redirect_u.trailing_slash = FALSE
                    THEN redirect_u.scheme || '://' || redirect_u.url
                ELSE redirect_u.url
            END AS redirect_url,
            redirect_uwm.status_code AS redirect_status_code,
            (lr.destination_url_id IS NOT NULL) AS has_redirect,
            (lr.destination_url_id IS NOT NULL AND redirect_uwm.status_code = 200) AS redirect_is_healthy,
            (uiapm.archive_url IS NOT NULL) AS has_archive,
            uiapm.archive_url
        FROM urls u
        LEFT JOIN url_web_metadata uwm
            ON uwm.url_id = u.id
        LEFT JOIN latest_redirect lr
            ON lr.source_url_id = u.id
        LEFT JOIN urls redirect_u
            ON redirect_u.id = lr.destination_url_id
        LEFT JOIN url_web_metadata redirect_uwm
            ON redirect_uwm.url_id = lr.destination_url_id
        LEFT JOIN url_internet_archives_probe_metadata uiapm
            ON uiapm.url_id = u.id
        """
    )


def upgrade() -> None:
    _create_url_health_view()


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS url_health_view")
