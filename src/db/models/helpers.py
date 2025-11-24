from sqlalchemy import Column, TIMESTAMP, func, Integer, ForeignKey, Enum as SAEnum, PrimaryKeyConstraint
from enum import Enum as PyEnum

def get_created_at_column() -> Column:
    return Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)


def get_agency_id_foreign_column(
    nullable: bool = False
) -> Column:
    return Column(
        'agency_id',
        Integer(),
        ForeignKey('agencies.id', ondelete='CASCADE'),
        nullable=nullable
    )

def enum_column(
    enum_type: type[PyEnum],
    name: str,
    nullable: bool = False
) -> Column[SAEnum]:
    return Column(
        SAEnum(
            enum_type,
            name=name,
            native_enum=True,
            values_callable=lambda enum_type: [e.value for e in enum_type]
        ),
        nullable=nullable
        )

def url_id_column() -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('urls.id', ondelete='CASCADE'),
        nullable=False
    )

def location_id_column() -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('locations.id', ondelete='CASCADE'),
        nullable=False
    )

CURRENT_TIME_SERVER_DEFAULT = func.now()

VIEW_ARG = {"info": "view"}

def url_id_primary_key_constraint() -> PrimaryKeyConstraint:
    return PrimaryKeyConstraint('url_id')


def county_column(nullable: bool = False) -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('counties.id', ondelete='CASCADE'),
        nullable=nullable
    )

def locality_column(nullable: bool = False) -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('localities.id', ondelete='CASCADE'),
        nullable=nullable
    )

def us_state_column(nullable: bool = False) -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('us_states.id', ondelete='CASCADE'),
        nullable=nullable
    )