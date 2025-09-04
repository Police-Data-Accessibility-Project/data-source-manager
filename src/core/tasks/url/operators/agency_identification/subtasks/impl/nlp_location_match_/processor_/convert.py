from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.mappings import \
    US_STATE_ISO_TO_NAME, US_NAME_TO_STATE_ISO
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.us_state import \
    USState


def convert_us_state_iso_to_us_state(iso: str) -> USState | None:
    name: str | None = US_STATE_ISO_TO_NAME.get(iso, None)

    if name is None:
        return None

    return USState(
        name=name,
        iso=iso
    )

def convert_us_state_name_to_us_state(name: str) -> USState | None:
    iso: str | None = US_NAME_TO_STATE_ISO.get(name, None)

    if iso is None:
        return None

    return USState(
        name=name,
        iso=iso
    )