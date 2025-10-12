"""
    CREATE OR REPLACE VIEW url_annotation_count AS
    with auto_location_count as (
    select
        u.id,
        count(anno.url_id) as cnt
    from urls u
    inner join public.auto_location_id_subtasks anno on u.id = anno.url_id
    group by u.id
)
, auto_agency_count as (
        select
        u.id,
        count(anno.url_id) as cnt
    from urls u
    inner join public.url_auto_agency_id_subtasks anno on u.id = anno.url_id
    group by u.id
)
, auto_url_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.auto_relevant_suggestions anno on u.id = anno.url_id
        group by u.id
)
, auto_record_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.auto_record_type_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_location_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_location_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_agency_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_url_agency_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_url_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_url_type_suggestions anno on u.id = anno.url_id
        group by u.id
        )
, user_record_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_record_type_suggestions anno on u.id = anno.url_id
        group by u.id
)
select
    u.id as url_id,
    coalesce(auto_ag.cnt, 0) as auto_agency_count,
    coalesce(auto_loc.cnt, 0) as auto_location_count,
    coalesce(auto_rec.cnt, 0) as auto_record_type_count,
    coalesce(auto_typ.cnt, 0) as auto_url_type_count,
    coalesce(user_ag.cnt, 0) as user_agency_count,
    coalesce(user_loc.cnt, 0) as user_location_count,
    coalesce(user_rec.cnt, 0) as user_record_type_count,
    coalesce(user_typ.cnt, 0) as user_url_type_count,
    (
    coalesce(auto_ag.cnt, 0) +
    coalesce(auto_loc.cnt, 0) +
    coalesce(auto_rec.cnt, 0) +
    coalesce(auto_typ.cnt, 0) +
    coalesce(user_ag.cnt, 0) +
    coalesce(user_loc.cnt, 0) +
    coalesce(user_rec.cnt, 0) +
    coalesce(user_typ.cnt, 0)
    ) as total_anno_count

    from urls u
    left join auto_agency_count auto_ag on auto_ag.id = u.id
    left join auto_location_count auto_loc on auto_loc.id = u.id
    left join auto_record_type_count auto_rec on auto_rec.id = u.id
    left join auto_url_type_count auto_typ on auto_typ.id = u.id
    left join user_agency_count user_ag on user_ag.id = u.id
    left join user_location_count user_loc on user_loc.id = u.id
    left join user_record_type_count user_rec on user_rec.id = u.id
    left join user_url_type_count user_typ on user_typ.id = u.id
"""
from sqlalchemy import PrimaryKeyConstraint, Column, Integer

from src.db.models.helpers import url_id_primary_key_constraint
from src.db.models.mixins import ViewMixin, URLDependentMixin
from src.db.models.templates_.base import Base


class URLAnnotationCount(
    Base,
    ViewMixin,
    URLDependentMixin
):

    __tablename__ = "url_annotation_count_view"
    __table_args__ = (
        url_id_primary_key_constraint(),
        {"info": "view"}
    )

    auto_agency_count = Column(Integer, nullable=False)
    auto_location_count = Column(Integer, nullable=False)
    auto_record_type_count = Column(Integer, nullable=False)
    auto_url_type_count = Column(Integer, nullable=False)
    user_agency_count = Column(Integer, nullable=False)
    user_location_count = Column(Integer, nullable=False)
    user_record_type_count = Column(Integer, nullable=False)
    user_url_type_count = Column(Integer, nullable=False)
    total_anno_count = Column(Integer, nullable=False)