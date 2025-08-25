from pydantic import BaseModel

from src.core.enums import RecordType
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.enums import \
    PushToHuggingFaceTestSetupStatusEnum


class TestPushToHuggingFaceURLSetupEntryInput(BaseModel):
    status: PushToHuggingFaceTestSetupStatusEnum
    record_type: RecordType | None
    has_html_content: bool
