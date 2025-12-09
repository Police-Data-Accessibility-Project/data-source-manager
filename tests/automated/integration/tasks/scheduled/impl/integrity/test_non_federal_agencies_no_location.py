import pytest

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator,
    pittsburgh_locality: LocalityCreationInfo
):
    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add federal agency
    agency = Agency(
        name="Federal Agency",
        agency_type=AgencyType.COURT,
        jurisdiction_type=JurisdictionType.FEDERAL
    )
    await operator.adb_client.add(agency)

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add non-federal agency
    agency = Agency(
        name="Non-Federal Agency",
        agency_type=AgencyType.COURT,
        jurisdiction_type=JurisdictionType.LOCAL
    )
    agency_id: int =await operator.adb_client.add(agency, return_id=True)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_view="integrity__non_federal_agencies_no_location_view"
    )

    # Add location to non-federal agency
    link = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=pittsburgh_locality.location_id
    )
    await operator.adb_client.add(link)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
