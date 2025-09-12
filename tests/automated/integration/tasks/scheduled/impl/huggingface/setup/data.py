from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput


def get_test_url(i: int) -> str:
    return f"www.testPushToHuggingFaceURLSetupEntry.com/{i}"

def get_test_html(i: int) -> str:
    return f"<html><div>Test Push to Hugging Face URL Setup Entry {i}</div></html>"

def generate_expected_outputs(
    url_ids: list[int],
    relevant: bool,
    record_type_fine: RecordType,
    record_type_coarse: RecordTypeCoarse
) -> list[GetForLoadingToHuggingFaceOutput]:
    results: list[GetForLoadingToHuggingFaceOutput] = []
    for i in range(2):
        output = GetForLoadingToHuggingFaceOutput(
            url_id=url_ids[i],
            url=get_test_url(i),
            relevant=relevant,
            record_type_fine=record_type_fine,
            record_type_coarse=record_type_coarse,
            html=get_test_html(i)
        )
        results.append(output)
    return results

