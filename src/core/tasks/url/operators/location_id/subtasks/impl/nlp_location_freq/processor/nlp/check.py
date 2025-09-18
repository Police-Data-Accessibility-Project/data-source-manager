from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.mappings import \
    US_STATE_ISO_TO_NAME, US_NAME_TO_STATE_ISO


def is_iso_us_state(iso: str) -> bool:
    return iso in US_STATE_ISO_TO_NAME

def is_name_us_state(name: str) -> bool:
    return name in US_NAME_TO_STATE_ISO