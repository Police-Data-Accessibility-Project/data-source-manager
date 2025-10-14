from src.core.tasks.url.operators.submit_approved.tdo import SubmittedURLInfo
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall


async def convert_to_task_errors(
    submitted_url_infos: list[SubmittedURLInfo]
) -> list[URLTaskErrorSmall]:
    task_errors: list[URLTaskErrorSmall] = []
    error_response_objects = [
        response_object for response_object in submitted_url_infos
        if response_object.request_error is not None
    ]
    for error_response_object in error_response_objects:
        error_info = URLTaskErrorSmall(
            url_id=error_response_object.url_id,
            error=error_response_object.request_error,
        )
        task_errors.append(error_info)
    return task_errors
