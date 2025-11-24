"""Add integrity monitor

Revision ID: 5ac9d50b91c5
Revises: 1bb2dfad3275
Create Date: 2025-11-23 19:23:45.487445

"""
from typing import Sequence, Union

from alembic import op

from src.util.alembic_helpers import add_enum_value

# revision identifiers, used by Alembic.
revision: str = '5ac9d50b91c5'
down_revision: Union[str, None] = '1bb2dfad3275'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    _create_integrity_task()
    _create_incomplete_data_sources_view()
    _create_incomplete_meta_urls_view()
    _create_url_both_data_source_and_meta_url_view()
    _create_non_federal_agencies_no_location_view()

def _create_non_federal_agencies_no_location_view():
    op.execute("""
    create view integrity__non_federal_agencies_no_location_view as
        select
            ag.name
        from agencies ag
        left join link_agencies__locations link on ag.id = link.agency_id
        where ag.jurisdiction_type != 'federal'
        and link.location_id is null
    """)


def _create_url_both_data_source_and_meta_url_view():
    op.execute("""
    create view integrity__url_both_data_source_and_meta_url_view
    select
        ds.url_id
    from
        ds_app_link_data_source ds
        join ds_app_link_meta_url mu
             on mu.url_id = ds.url_id
    """)


def _create_incomplete_meta_urls_view():
    op.execute("""
    create view integrity__incomplete_data_sources_view as
    select
        mu.url_id,
        fuv.url_id is not null as has_validated_flag,
        fuv.type as validated_type
    from ds_app_link_meta_url mu
    left join flag_url_validated fuv on fuv.url_id = mu.url_id
    left join url_record_type urt on urt.url_id = mu.url_id
    where
        fuv.url_id is null
    or fuv.type != 'meta url'
    or urt.url_id is null
    """)


def _create_incomplete_data_sources_view():
    op.execute("""
    create view integrity__incomplete_data_sources_view as
        select
            mu.url_id,
            fuv.url_id is not null as has_validated_flag,
            fuv.type as validated_type,
            urt.url_id is not null as has_record_type
        
        from ds_app_link_meta_url mu
        left join flag_url_validated fuv on fuv.url_id = mu.url_id
        left join url_record_type urt on urt.url_id = mu.url_id
        where
            fuv.url_id is null
        or fuv.type != 'data source'
        or urt.url_id is null
    """)


def _create_integrity_task():
    add_enum_value(
        enum_name="task_type",
        enum_value="Integrity Monitor",
    )


def downgrade() -> None:
    pass
