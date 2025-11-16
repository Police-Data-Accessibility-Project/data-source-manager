from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation


async def add_agency(
    adb_client: AsyncDatabaseClient,
    location_id: int
) -> int:
    agency_1 = Agency(
        name="Agency 1",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.STATE,
    )
    agency_id: int = await adb_client.add(agency_1, return_id=True)
    # Add Agency location
    agency_1_location = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=location_id,
    )
    await adb_client.add(agency_1_location)
    return agency_id
