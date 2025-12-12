"""
Add a URL with two of the same suggestions for each of the following:
- Agency
- Location
- Record Type
- URL Type (DATA SOURCE)
And confirm it is validated as DATA SOURCE
"""
from uuid import UUID

import pytest

from src.core.enums import RecordType
from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.anonymous_sessions__name_suggestion import LinkAnonymousSessionNameSuggestion
from src.db.models.impl.url.suggestion.anonymous.agency.sqlalchemy import AnonymousAnnotationAgency
from src.db.models.impl.url.suggestion.anonymous.location.sqlalchemy import AnonymousAnnotationLocation
from src.db.models.impl.url.suggestion.anonymous.record_type.sqlalchemy import AnonymousAnnotationRecordType
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper, DEFAULT_RECORD_TYPE
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_data_source(
    operator: AutoValidateURLTaskOperator,
    helper: TestValidateTaskHelper
):
    await helper.add_url_type_suggestions(
        url_type=URLType.DATA_SOURCE,
        count=2
    )

    assert not await operator.meets_task_prerequisites()

    await helper.add_agency_suggestions(count=1)

    assert not await operator.meets_task_prerequisites()

    await helper.add_location_suggestions(count=1)

    assert not await operator.meets_task_prerequisites()

    await helper.add_record_type_suggestions(count=1)

    assert not await operator.meets_task_prerequisites()

    suggestion_id: int = await helper.add_name_suggestion(count=1)

    assert not await operator.meets_task_prerequisites()

    # Add anonymous annotations
    session_id_1: UUID = await helper.get_anonymous_session_id()
    session_id_2: UUID = await helper.get_anonymous_session_id()

    for session_id in [session_id_1, session_id_2]:
        anon_url_type = AnonymousAnnotationURLType(
            url_type=URLType.DATA_SOURCE,
            session_id=session_id,
            url_id=helper.url_id
        )
        anon_record_type = AnonymousAnnotationRecordType(
            record_type=DEFAULT_RECORD_TYPE,
            session_id=session_id,
            url_id=helper.url_id
        )
        anon_location = AnonymousAnnotationLocation(
            location_id=helper.location_id,
            session_id=session_id,
            url_id=helper.url_id
        )
        anon_agency = AnonymousAnnotationAgency(
            agency_id=helper.agency_id,
            session_id=session_id,
            url_id=helper.url_id
        )
        anon_name_link = LinkAnonymousSessionNameSuggestion(
            suggestion_id=suggestion_id,
            session_id=session_id
        )
        for model in [
            anon_url_type,
            anon_record_type,
            anon_location,
            anon_agency,
            anon_name_link
        ]:
            await helper.adb_client.add(model)

    assert await operator.meets_task_prerequisites()

    # Add different record type suggestion
    await helper.add_record_type_suggestions(
        count=2,
        record_type=RecordType.STOPS
    )

    # Assert no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add tiebreaker -- a single anonymous vote
    session_id_3: UUID = await helper.get_anonymous_session_id()
    anon_record_type = AnonymousAnnotationRecordType(
        record_type=DEFAULT_RECORD_TYPE,
        session_id=session_id_3,
        url_id=helper.url_id
    )
    await helper.adb_client.add(anon_record_type)

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    await helper.check_url_validated(URLType.DATA_SOURCE)
    await helper.check_auto_validated()
    await helper.check_agency_linked()
    await helper.check_record_type()
    await helper.check_name()

