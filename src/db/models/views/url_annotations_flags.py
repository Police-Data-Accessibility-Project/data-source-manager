"""
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
         LEFT JOIN public.annotation__auto__record_type arts ON u.id = arts.url_id
         LEFT JOIN public.annotation__auto__url_type ars ON u.id = ars.url_id
         LEFT JOIN public.{URL_AUTO_AGENCY_SUGGESTIONS_TABLE_NAME} auas ON u.id = auas.url_id
         LEFT JOIN public.annotation__user__record_type urts ON u.id = urts.url_id
         LEFT JOIN public.annotation__user__url_type urs ON u.id = urs.url_id
         LEFT JOIN public.annotation__user__agency uuas ON u.id = uuas.url_id
         LEFT JOIN public.reviewing_user_url ruu ON u.id = ruu.url_id
         LEFT JOIN public.link_agencies__urls cua on u.id = cua.url_id
    )
"""

from sqlalchemy import PrimaryKeyConstraint, Column, Boolean

from src.db.models.mixins import ViewMixin, URLDependentMixin, URLDependentViewMixin
from src.db.models.templates_.base import Base


class URLAnnotationFlagsView(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "url_annotation_flags"

    has_auto_record_type_suggestion = Column(Boolean, nullable=False)
    has_auto_relevant_suggestion = Column(Boolean, nullable=False)
    has_auto_agency_suggestion = Column(Boolean, nullable=False)
    has_auto_location_suggestion = Column(Boolean, nullable=False)
    has_user_record_type_suggestion = Column(Boolean, nullable=False)
    has_user_relevant_suggestion = Column(Boolean, nullable=False)
    has_user_agency_suggestion = Column(Boolean, nullable=False)
    has_user_location_suggestion = Column(Boolean, nullable=False)
    has_confirmed_agency = Column(Boolean, nullable=False)
    was_reviewed = Column(Boolean, nullable=False)