"""Add url scheme column

Revision ID: a8f36f185694
Revises: 7aace6587d1a
Create Date: 2025-10-14 11:05:28.686940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f36f185694'
down_revision: Union[str, None] = '7aace6587d1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    _update_foreign_key_constraints()

    _delete_duplicate_urls()
    _add_column()
    _populate_column()
    _remove_schemes_from_url_column()
    _add_check_constraint_to_url_column()

def _update_foreign_key_constraints():
    # URL Optional Data Source Metadata
    op.execute("""
       ALTER TABLE url_optional_data_source_metadata
       DROP CONSTRAINT IF EXISTS url_optional_data_source_metadata_url_id_fkey;
   """)

    op.create_foreign_key(
        "url_optional_data_source_metadata_url_id_fkey",
        "url_optional_data_source_metadata",
        "urls",
        ["url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Link URLs Redirect URL
    # (Source URL ID)
    op.execute("""
       ALTER TABLE link_urls_redirect_url
       DROP CONSTRAINT IF EXISTS link_urls_redirect_url_source_url_id_fkey;
   """)

    op.create_foreign_key(
        "link_urls_redirect_url_source_url_id_fkey",
        "link_urls_redirect_url",
        "urls",
        ["source_url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # (Destination URL ID)
    op.execute("""
       ALTER TABLE link_urls_redirect_url
       DROP CONSTRAINT IF EXISTS link_urls_redirect_url_destination_url_id_fkey;
   """)

    op.create_foreign_key(
        "link_urls_redirect_url_destination_url_id_fkey",
        "link_urls_redirect_url",
        "urls",
        ["destination_url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Reviewing User URL
    op.execute("""
       ALTER TABLE reviewing_user_url
       DROP CONSTRAINT IF EXISTS approving_user_url_url_id_fkey;
   """)

    op.create_foreign_key(
        "approving_user_url_url_id_fkey",
        "reviewing_user_url",
        "urls",
        ["url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # user_url_agency_suggestions
    op.execute("""
       ALTER TABLE user_url_agency_suggestions
       DROP CONSTRAINT IF EXISTS user_url_agency_suggestions_url_id_fkey;
   """)

    op.create_foreign_key(
        "user_url_agency_suggestions_url_id_fkey",
        "user_url_agency_suggestions",
        "urls",
        ["url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Duplicates
    op.execute("""
       ALTER TABLE duplicates
       DROP CONSTRAINT IF EXISTS duplicates_original_url_id_fkey;
   """)

    op.create_foreign_key(
        "duplicates_original_url_id_fkey",
        "duplicates",
        "urls",
        ["original_url_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # link_user_name_suggestions
    op.execute("""
       ALTER TABLE link_user_name_suggestions
       DROP CONSTRAINT IF EXISTS link_user_name_suggestions_suggestion_id_fkey;
   """)

    op.create_foreign_key(
        "link_user_name_suggestions_suggestion_id_fkey",
        "link_user_name_suggestions",
        "url_name_suggestions",
        ["suggestion_id"],
        ["id"],
        ondelete="CASCADE"
    )

def _delete_duplicate_urls():
    op.execute("""
    DELETE FROM urls
        WHERE id IN (
            4217,
            15902,
            3472,
            17387,
            24256,
            17617,
            17414,
            15259,
            17952,
            17651,
            18010,
            18496,
            18563,
            18587,
            18592,
            18092,
            18046,
            20467,
            24346,
            28241,
            25075,
            22508,
            22391,
            24256,
            22486,
            28109,
            26336,
            30701,
            17387,
            19348,
            18080,
            27863,
            18855,
            28830,
            18824,
            17414,
            15259,
            20676,
            27716,
            21475,
            23442,
            28553,
            8176,
            22270,
            19161,
            21250,
            15659,
            18821,
            27067,
            27567,
            27318,
            20640,
            21840,
            3472,
            28982,
            28910,
            19527,
            28776,
            15902,
            18468,
            29557,
            22977,
            27694,
            22678,
            19094,
            27203,
            26436,
            18868,
            22813,
            25007,
            7548,
            30088,
            20924,
            22575,
            28149,
            30705,
            28179,
            30660,
            2988,
            17182,
            18893,
            30317,
            19215,
            17651,
            21117,
            17617,
            23742,
            19620,
            16865,
            19320,
            20516,
            25248,
            26122,
            30158,
            30522,
            23307,
            18621,
            27855,
            26922,
            21397,
            18010,
            18592,
            2527,
            26279,
            18563,
            18242,
            21550,
            28288,
            22361,
            24660,
            2989,
            28765,
            10627,
            19625,
            12191,
            27523,
            18373,
            28565,
            25437,
            26077,
            28554,
            23229,
            25631,
            25528,
            18092,
            10765,
            26126,
            51499,
            27375,
            24177,
            22734,
            22459,
            22439,
            18532,
            29064,
            20504,
            21643,
            21551,
            27698,
            19234,
            24308,
            22559,
            26227,
            19080,
            16010,
            3515,
            22658,
            20673,
            21854,
            19361,
            21768,
            26903,
            21253,
            23085,
            3761,
            3565
            )
    """)

def _populate_column():
    op.execute(
        """
        UPDATE urls
        SET scheme = lower(split_part(url, '://', 1))
        WHERE url ~* '^[a-z][a-z0-9+.-]*://';
        """
    )


def _remove_schemes_from_url_column():
    op.execute(
        """
        UPDATE urls
        SET url = regexp_replace(url, '^[a-z][a-z0-9+.-]*://', '', 'i')
        WHERE url ~* '^[a-z][a-z0-9+.-]*://';
        """
    )


def _add_check_constraint_to_url_column():
    op.execute(
        """
        ALTER TABLE urls
        ADD CONSTRAINT check_url_does_not_have_schema CHECK (url !~* '^[a-z][a-z0-9+.-]*://');
        """
    )


def _add_column():
    op.add_column(
        "urls",
        sa.Column("scheme", sa.String(), nullable=True)
    )

def downgrade() -> None:
    pass
