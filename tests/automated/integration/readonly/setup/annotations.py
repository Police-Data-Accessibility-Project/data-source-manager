from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.url_type.user import UserURLTypeSuggestion


async def add_full_data_sources_annotations(
    url_id: int,
    user_id: int,
    agency_id: int,
    location_id: int,
    adb_client: AsyncDatabaseClient
) -> None:
    name_suggestion = URLNameSuggestion(
        url_id=url_id,
        suggestion="Name suggestion",
        source=NameSuggestionSource.USER
    )
    name_suggestion_id: int = await adb_client.add(
        name_suggestion,
        return_id=True
    )
    url_type_suggestion = UserURLTypeSuggestion(
        url_id=url_id,
        user_id=user_id,
        type=URLType.DATA_SOURCE
    )
    record_type_suggestion = UserRecordTypeSuggestion(
        user_id=user_id,
        url_id=url_id,
        record_type=RecordType.RECORDS_REQUEST_INFO.value
    )
    user_name_suggestion = LinkUserNameSuggestion(
        user_id=user_id,
        suggestion_id=name_suggestion_id,
    )
    agency_suggestion = UserURLAgencySuggestion(
        agency_id=agency_id,
        url_id=url_id,
        user_id=user_id,
    )
    location_suggestion = UserLocationSuggestion(
        location_id=location_id,
        url_id=url_id,
        user_id=user_id,
    )
    for suggestion in [
        url_type_suggestion,
        record_type_suggestion,
        user_name_suggestion,
        agency_suggestion,
        location_suggestion
    ]:
        await adb_client.add(suggestion)

async def add_minimal_not_relevant_annotation(
    url_id: int,
    user_id: int,
    adb_client: AsyncDatabaseClient
) -> None:
    url_type_suggestion = UserURLTypeSuggestion(
        url_id=url_id,
        user_id=user_id,
        type=URLType.NOT_RELEVANT
    )
    await adb_client.add(url_type_suggestion)