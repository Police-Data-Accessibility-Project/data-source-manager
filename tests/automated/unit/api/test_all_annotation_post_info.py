import pytest
from pydantic import BaseModel

from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import RecordType
from src.core.exceptions import FailedValidationException
from src.db.models.impl.flag.url_validated.enums import URLType


class TestAllAnnotationPostInfoParams(BaseModel):
    suggested_status: URLType
    record_type: RecordType | None
    agency_ids: list[int]
    location_ids: list[int]
    raise_exception: bool

@pytest.mark.parametrize(
    "params",
    [
        # Happy Paths
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.META_URL,
            record_type=None,
            agency_ids=[1, 2],
            location_ids=[3,4],
            raise_exception=False
        ),
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[1, 2],
            location_ids=[3,4],
            raise_exception=False
        ),
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.NOT_RELEVANT,
            record_type=None,
            agency_ids=[],
            location_ids=[],
            raise_exception=False
        ),
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.INDIVIDUAL_RECORD,
            record_type=None,
            agency_ids=[1, 2],
            location_ids=[3, 4],
            raise_exception=False
        ),
        # Error Paths - Meta URL
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.META_URL,
            record_type=RecordType.ACCIDENT_REPORTS,  # Record Type Included
            agency_ids=[1, 2],
            location_ids=[3, 4],
            raise_exception=True
        ),
        # Error Paths - Not Relevant
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.NOT_RELEVANT,
            record_type=RecordType.ACCIDENT_REPORTS,  # Record Type Included
            agency_ids=[],
            location_ids=[],
            raise_exception=True
        ),
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.NOT_RELEVANT,
            record_type=None,
            agency_ids=[1, 2],  # Agency IDs Included
            location_ids=[],
            raise_exception=True
        ),
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.NOT_RELEVANT,
            record_type=None,
            agency_ids=[],
            location_ids=[1, 2],  # Location IDs included
            raise_exception=True
        ),
        # Error Paths - Individual Record
        TestAllAnnotationPostInfoParams(
            suggested_status=URLType.INDIVIDUAL_RECORD,
            record_type=RecordType.ACCIDENT_REPORTS,  # Record Type Included
            agency_ids=[],
            location_ids=[],
            raise_exception=True
        ),
    ]
)
def test_all_annotation_post_info(
    params: TestAllAnnotationPostInfoParams
):
    if params.raise_exception:
        with pytest.raises(FailedValidationException):
            AllAnnotationPostInfo(
                suggested_status=params.suggested_status,
                record_type=params.record_type,
                agency_info=AnnotationPostAgencyInfo(agency_ids=params.agency_ids),
                location_info=AnnotationPostLocationInfo(location_ids=params.location_ids)
            )
    else:
        AllAnnotationPostInfo(
            suggested_status=params.suggested_status,
            record_type=params.record_type,
            agency_info=AnnotationPostAgencyInfo(agency_ids=params.agency_ids),
            location_info=AnnotationPostLocationInfo(location_ids=params.location_ids)
        )