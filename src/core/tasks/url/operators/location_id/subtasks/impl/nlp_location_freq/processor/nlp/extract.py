from collections import Counter

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.constants import \
    TOP_N_LOCATIONS_COUNT
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models.us_state import \
    USState


def extract_most_common_us_state(
    us_state_counter: Counter[USState]
) -> USState | None:
    try:
        return us_state_counter.most_common(1)[0][0]
    except IndexError:
        return None

def extract_top_n_locations(
    location_counter: Counter[str]
) -> list[str]:
    top_n_locations_raw: list[tuple[str, int]] = \
        location_counter.most_common(TOP_N_LOCATIONS_COUNT)
    top_n_locations: list[str] = []
    for location, _ in top_n_locations_raw:
        top_n_locations.append(location)
    return top_n_locations