"""Add missing location/agency URL status

Revision ID: c4f9bbf8a201
Revises: 1fb2286a016c
Create Date: 2026-02-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c4f9bbf8a201"
down_revision: Union[str, None] = "1fb2286a016c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_url_status_mat_view() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW url_status_mat_view AS
        WITH
            urls_with_relevant_errors AS (
                SELECT
                    ute.url_id
                FROM
                    url_task_error ute
                WHERE
                    ute.task_type = ANY (
                        ARRAY[
                            'Screenshot'::task_type,
                            'HTML'::task_type,
                            'URL Probe'::task_type
                        ]
                    )
            ),
            unresolved_missing_queue AS (
                SELECT
                    fus.url_id
                FROM
                    flag_url_suspended fus
                    LEFT JOIN link_user_suggestion_location_not_found luslnf
                        ON luslnf.url_id = fus.url_id
                    LEFT JOIN link_user_suggestion_agency_not_found lusanf
                        ON lusanf.url_id = fus.url_id
                GROUP BY
                    fus.url_id
                HAVING
                    count(luslnf.user_id) >= 2
                    OR count(lusanf.user_id) >= 2
            ),
            status_text AS (
                SELECT
                    u.id AS url_id,
                    CASE
                        WHEN fuv.type = ANY (
                            ARRAY[
                                'not relevant'::url_type,
                                'individual record'::url_type,
                                'not found'::url_type
                            ]
                        ) THEN 'Accepted'::text
                        WHEN (
                            fuv.type = 'data source'::url_type
                            AND uds.url_id IS NULL
                        ) OR (
                            fuv.type = 'meta url'::url_type
                            AND udmu.url_id IS NULL
                        ) THEN 'Awaiting Submission'::text
                        WHEN (
                            fuv.type = 'data source'::url_type
                            AND uds.url_id IS NOT NULL
                        ) OR (
                            fuv.type = 'meta url'::url_type
                            AND udmu.url_id IS NOT NULL
                        ) THEN 'Submitted'::text
                        WHEN fuv.type IS NULL AND umq.url_id IS NOT NULL THEN 'Missing Location / Agency'::text
                        WHEN uch.url_id IS NOT NULL
                            AND uwm.url_id IS NOT NULL
                            AND us.url_id IS NOT NULL THEN 'Community Labeling'::text
                        WHEN uwre.url_id IS NOT NULL THEN 'Error'::text
                        ELSE 'Intake'::text
                    END AS status
                FROM
                    urls u
                    LEFT JOIN urls_with_relevant_errors uwre
                        ON u.id = uwre.url_id
                    LEFT JOIN url_screenshot us
                        ON u.id = us.url_id
                    LEFT JOIN url_compressed_html uch
                        ON u.id = uch.url_id
                    LEFT JOIN url_web_metadata uwm
                        ON u.id = uwm.url_id
                    LEFT JOIN flag_url_validated fuv
                        ON u.id = fuv.url_id
                    LEFT JOIN ds_app_link_meta_url udmu
                        ON u.id = udmu.url_id
                    LEFT JOIN ds_app_link_data_source uds
                        ON u.id = uds.url_id
                    LEFT JOIN unresolved_missing_queue umq
                        ON u.id = umq.url_id
            )
        SELECT
            status_text.url_id,
            status_text.status,
            CASE status_text.status
                WHEN 'Intake'::text THEN 100
                WHEN 'Error'::text THEN 110
                WHEN 'Community Labeling'::text THEN 200
                WHEN 'Accepted'::text THEN 300
                WHEN 'Missing Location / Agency'::text THEN 320
                WHEN 'Awaiting Submission'::text THEN 380
                WHEN 'Submitted'::text THEN 390
                ELSE '-1'::integer
            END AS code
        FROM
            status_text;
        """
    )


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS url_status_mat_view")
    _create_url_status_mat_view()


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS url_status_mat_view")
    op.execute(
        """
        CREATE MATERIALIZED VIEW url_status_mat_view AS
        WITH
            urls_with_relevant_errors AS (
                SELECT
                    ute.url_id
                FROM
                    url_task_error ute
                WHERE
                    ute.task_type = ANY (ARRAY ['Screenshot'::task_type, 'HTML'::task_type, 'URL Probe'::task_type])
            ),
            status_text AS (
                SELECT
                    u.id AS url_id,
                    CASE
                        WHEN fuv.type = ANY (
                            ARRAY['not relevant'::url_type, 'individual record'::url_type, 'not found'::url_type]
                        ) THEN 'Accepted'::text
                        WHEN fuv.type = 'data source'::url_type AND uds.url_id IS NULL OR
                             fuv.type = 'meta url'::url_type AND udmu.url_id IS NULL THEN 'Awaiting Submission'::text
                        WHEN fuv.type = 'data source'::url_type AND uds.url_id IS NOT NULL OR
                             fuv.type = 'meta url'::url_type AND udmu.url_id IS NOT NULL THEN 'Submitted'::text
                        WHEN uch.url_id IS NOT NULL AND uwm.url_id IS NOT NULL AND us.url_id IS NOT NULL
                            THEN 'Community Labeling'::text
                        WHEN uwre.url_id IS NOT NULL THEN 'Error'::text
                        ELSE 'Intake'::text
                    END AS status
                FROM
                    urls u
                    LEFT JOIN urls_with_relevant_errors uwre
                        ON u.id = uwre.url_id
                    LEFT JOIN url_screenshot us
                        ON u.id = us.url_id
                    LEFT JOIN url_compressed_html uch
                        ON u.id = uch.url_id
                    LEFT JOIN url_web_metadata uwm
                        ON u.id = uwm.url_id
                    LEFT JOIN flag_url_validated fuv
                        ON u.id = fuv.url_id
                    LEFT JOIN ds_app_link_meta_url udmu
                        ON u.id = udmu.url_id
                    LEFT JOIN ds_app_link_data_source uds
                        ON u.id = uds.url_id
            )
        SELECT
            status_text.url_id,
            status_text.status,
            CASE status_text.status
                WHEN 'Intake'::text THEN 100
                WHEN 'Error'::text THEN 110
                WHEN 'Community Labeling'::text THEN 200
                WHEN 'Accepted'::text THEN 300
                WHEN 'Awaiting Submission'::text THEN 380
                WHEN 'Submitted'::text THEN 390
                ELSE '-1'::integer
            END AS code
        FROM
            status_text;
        """
    )
