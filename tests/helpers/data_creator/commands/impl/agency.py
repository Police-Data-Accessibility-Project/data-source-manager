from random import randint
from typing import final

from typing_extensions import override

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.simple_test_data_functions import generate_test_name


@final
class AgencyCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        name: str | None = None
    ):
        super().__init__()
        if name is None:
            name = generate_test_name()
        self.name = name

    @override
    async def run(self) -> int:
        agency_id = randint(1, 99999999)
        await self.adb_client.upsert_new_agencies(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=-1,
                    suggestion_type=SuggestionType.UNKNOWN,
                    pdap_agency_id=agency_id,
                    agency_name=self.name,
                    state=f"Test State {agency_id}",
                    county=f"Test County {agency_id}",
                    locality=f"Test Locality {agency_id}"
                )
            ]
        )
        return agency_id
