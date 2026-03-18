import pytest
from sqlalchemy import delete, select

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db import Location
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.impl.location.location.enums import LocationType
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
    agency_id: int = await operator.adb_client.add(agency, return_id=True)

    # Add US national location link
    national_location_id = await operator.adb_client.scalar(
        select(
            Location.id
        ).where(
            Location.type == LocationType.NATIONAL
        )
    )
    if national_location_id is None:
        national_location_id = await operator.adb_client.add(
            Location(type=LocationType.NATIONAL),
            return_id=True
        )

    national_link = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=national_location_id
    )
    await operator.adb_client.add(national_link)

    # Check still does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add non-national location link for same federal agency
    bad_link = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=pittsburgh_locality.location_id
    )
    await operator.adb_client.add(bad_link)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_view="integrity__federal_agencies_wrong_location_view"
    )

    # Remove non-national link
    statement = (
        delete(
            LinkAgencyLocation
        ).where(
            LinkAgencyLocation.agency_id == agency_id,
            LinkAgencyLocation.location_id == pittsburgh_locality.location_id
        )
    )
    await operator.adb_client.execute(statement)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
