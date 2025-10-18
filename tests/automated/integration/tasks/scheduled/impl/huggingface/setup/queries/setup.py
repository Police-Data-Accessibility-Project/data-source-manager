from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import compress_html
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.data import get_test_url, get_test_html
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.enums import \
    PushToHuggingFaceTestSetupStatusEnum
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.queries.convert import \
    convert_test_status_to_validated_status


class SetupTestPushToHuggingFaceEntryQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        inp: TestPushToHuggingFaceURLSetupEntryInput
    ):
        super().__init__()
        self.inp = inp

    async def run(self, session: AsyncSession) -> list[int]:
        url_ids: list[int] = []
        for i in range(2):
            if i % 2 == 0:
                name = "Test Push to Hugging Face URL Setup Entry"
                description = "This is a test push to Hugging Face URL setup entry"
            else:
                name = None
                description = None
            url = URL(
                url=get_test_url(i),
                scheme=None,
                status=URLStatus.OK,
                name=name,
                description=description,
                source=URLSource.COLLECTOR,
                trailing_slash=False,
            )
            session.add(url)
            await session.flush()
            record_type = URLRecordType(
                url_id=url.id,
                record_type=self.inp.record_type,
            )
            session.add(record_type)
            url_ids.append(url.id)
            if self.inp.status in (
                PushToHuggingFaceTestSetupStatusEnum.DATA_SOURCE,
                PushToHuggingFaceTestSetupStatusEnum.NOT_RELEVANT
            ):
                flag = FlagURLValidated(
                    url_id=url.id,
                    type=convert_test_status_to_validated_status(self.inp.status),
                )
                session.add(flag)

            if self.inp.has_html_content:
                compressed_html = URLCompressedHTML(
                    url_id=url.id,
                    compressed_html=compress_html(get_test_html(i)),
                )
                session.add(compressed_html)

        return url_ids

