from src.core.tasks.url.operators.submit_approved.tdo import SubmittedURLInfo


async def filter_successes(
    submitted_url_infos: list[SubmittedURLInfo]
) -> list[SubmittedURLInfo]:
    success_infos = [
        response_object for response_object in submitted_url_infos
        if response_object.data_source_id is not None
    ]
    return success_infos
