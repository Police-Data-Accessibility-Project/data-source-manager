import pytest

from src.api.endpoints.review.enums import RejectionReason
from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from tests.automated.integration.api.review.rejection.helpers import run_rejection_test


@pytest.mark.asyncio
async def test_rejection_not_relevant(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.NOT_RELEVANT,
        url_status=URLStatus.OK
    )

    # Get FlagURLValidated and confirm Not Relevant
    flag: FlagURLValidated = (await api_test_helper.adb_client().get_all(FlagURLValidated))[0]
    assert flag.type == URLType.NOT_RELEVANT