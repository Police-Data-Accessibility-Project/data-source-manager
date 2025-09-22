import pytest_asyncio

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest_asyncio.fixture
async def batch_url_creation_info(db_data_creator):

    parameters = TestBatchCreationParameters(
        urls=[
            TestURLCreationParameters(
                count=2,
                status=URLCreationEnum.OK,
                annotation_info=AnnotationInfo(
                    user_relevant=URLType.DATA_SOURCE,
                    user_record_type=RecordType.ARREST_RECORDS,
                    user_agency=URLAgencyAnnotationPostInfo(
                        suggested_agency=await db_data_creator.agency()
                    )
                )
            )
        ]
    )

    return await db_data_creator.batch_v2(parameters=parameters)
