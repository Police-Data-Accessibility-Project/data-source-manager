from src.external.pdap.enums import DataSourcesURLStatus
from src.db.models.materialized_views.url_health.enums import URLHealthViewEnum


def convert_sm_url_status_to_ds_url_status(
    status_code: int | None
) -> DataSourcesURLStatus:
    match status_code:
        case 200:
            return DataSourcesURLStatus.OK
        case _:
            return DataSourcesURLStatus.BROKEN


def convert_sm_url_health_to_ds_url_status(
    health: URLHealthViewEnum | str | None,
    has_archive: bool,
) -> DataSourcesURLStatus:
    if health == URLHealthViewEnum.OK.value:
        return DataSourcesURLStatus.OK
    if has_archive:
        return DataSourcesURLStatus.AVAILABLE
    return DataSourcesURLStatus.BROKEN
