from src.db.models.impl.annotation.location.auto.subtask.constants import MAX_SUGGESTION_LENGTH


def clean_title(title: str) -> str:
    if len(title) > MAX_SUGGESTION_LENGTH:
        return title[:MAX_SUGGESTION_LENGTH-3] + "..."
    return title