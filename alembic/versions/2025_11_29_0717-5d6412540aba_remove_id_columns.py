"""Remove ID columns

Revision ID: 5d6412540aba
Revises: d5f0cc2be6b6
Create Date: 2025-11-29 07:17:32.794305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d6412540aba'
down_revision: Union[str, None] = 'd5f0cc2be6b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "task_errors",  #
    "auto_record_type_suggestions",  #
    "auto_relevant_suggestions",  #
    "duplicates",  #
    "flag_url_validated",  #
    "link_agencies__locations",  #
    "link_urls_redirect_url",  #
    "link_urls_root_url",  #
    "reviewing_user_url",  #
    "url_checked_for_duplicate",  #
    "url_compressed_html", #
    "url_html_content",  #
    "url_internet_archives_probe_metadata",  #
    "url_internet_archives_save_metadata",  #
    "url_optional_data_source_metadata",  #
    "url_scrape_info",  #
    "url_web_metadata",  #
    "user_record_type_suggestions",  #
    "user_url_type_suggestions",  #
]

URL_ONLY_PRIMARY_KEY_TABLES = [
    "url_checked_for_duplicate",  #
    "url_compressed_html",  #
    "url_internet_archives_probe_metadata",  #
    "url_internet_archives_save_metadata",  #
    "url_optional_data_source_metadata",  #
    "url_scrape_info",  #
    "url_web_metadata",  #
    "auto_relevant_suggestions",  #
    "auto_record_type_suggestions",  #
    "flag_url_validated"  #
]



USER_URL_ID_PRIMARY_KEY_TABLES = [
    "user_record_type_suggestions",  #
    "user_url_type_suggestions",  #
    "reviewing_user_url"  #
]

BESPOKE_UNIQUE_IDS: dict[str, list[str]] = {
    "task_errors": ["task_id"],  #
    "link_agencies__locations": ["agency_id", "location_id"],  #
    "link_urls_redirect_url": ["source_url_id", "destination_url_id"],  #
    "link_urls_root_url": ["url_id", "root_url_id"],  #
    "url_html_content": ["url_id", "content_type"],  #
}

def drop_views():
    op.execute("drop materialized view if exists url_status_mat_view")
    op.execute("drop materialized view if exists batch_url_status_mat_view")

def recreate_views():
    op.execute("""
    create materialized view url_status_mat_view as
    WITH
        urls_with_relevant_errors AS (
            SELECT
                ute.url_id
            FROM
                url_task_error ute
            WHERE
                ute.task_type = ANY (ARRAY ['Screenshot'::task_type, 'HTML'::task_type, 'URL Probe'::task_type])
            )
        , status_text AS (
            SELECT
                u.id AS url_id,
                CASE
                    WHEN fuv.type = ANY
                         (ARRAY ['not relevant'::url_type, 'individual record'::url_type, 'not found'::url_type])
                        THEN 'Accepted'::text
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
    """)

    op.execute("""
    create materialized view batch_url_status_mat_view as
    WITH
        batches_with_urls AS (
            SELECT
                b_1.id
            FROM
                batches b_1
            WHERE
                (EXISTS (
                    SELECT
                        1
                    FROM
                        link_batches__urls lbu
                    WHERE
                        lbu.batch_id = b_1.id
                    ))
            )
        , batches_with_only_validated_urls AS (
            SELECT
                b_1.id
            FROM
                batches b_1
            WHERE
                (EXISTS (
                    SELECT
                        1
                    FROM
                        link_batches__urls lbu
                        LEFT JOIN flag_url_validated fuv
                                  ON fuv.url_id = lbu.url_id
                    WHERE
                        lbu.batch_id = b_1.id
                        AND fuv.url_id IS NOT NULL
                    ))
                AND NOT (EXISTS (
                    SELECT
                        1
                    FROM
                        link_batches__urls lbu
                        LEFT JOIN flag_url_validated fuv
                                  ON fuv.url_id = lbu.url_id
                    WHERE
                        lbu.batch_id = b_1.id
                        AND fuv.url_id IS NULL
                    ))
            )
    SELECT
        b.id AS batch_id,
        CASE
            WHEN b.status = 'error'::batch_status THEN 'Error'::text
            WHEN bwu.id IS NULL THEN 'No URLs'::text
            WHEN bwovu.id IS NOT NULL THEN 'Labeling Complete'::text
            ELSE 'Has Unlabeled URLs'::text
            END AS batch_url_status
    FROM
        batches b
        LEFT JOIN batches_with_urls bwu
                  ON bwu.id = b.id
        LEFT JOIN batches_with_only_validated_urls bwovu
                  ON bwovu.id = b.id;
    """)



def upgrade() -> None:
    drop_views()

    for table in TABLES:
        op.drop_column(table, "id")

    # Add new primary keys
    for table, columns in BESPOKE_UNIQUE_IDS.items():
        suffix = "_".join(columns)
        op.create_primary_key(
            f"pk_{table}_{suffix}",
            table,
            columns
        )

    for table in URL_ONLY_PRIMARY_KEY_TABLES:
        op.create_primary_key(
            f"pk_{table}",
            table,
            ["url_id"]
        )

    for table in USER_URL_ID_PRIMARY_KEY_TABLES:
        op.create_primary_key(
            f"pk_{table}",
            table,
            ["user_id", "url_id"]
        )

    recreate_views()





def downgrade() -> None:
    pass
