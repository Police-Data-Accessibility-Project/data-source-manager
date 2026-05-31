from src.api.shared.models.request_base import RequestBase


class ResolveMissingAnnotationRequest(RequestBase):
    location_id: int
    agency_id: int
