from collections import Counter
from typing import Mapping

from spacy import Language
from spacy.tokens import Doc

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.check import \
    is_name_us_state, is_iso_us_state
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.convert import \
    convert_us_state_name_to_us_state, convert_us_state_iso_to_us_state
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.us_state import \
    USState


class NLPProcessor:

    def __init__(
        self,
        model: Language
    ):
        self._model: Language = model

    def parse_for_locations(self, html: str) -> NLPLocationMatchResponse:
        doc: Doc = self._model(html)
        us_state_counter: Counter[USState] = Counter()
        location_counter: Counter[str] = Counter()

        for ent in doc.ents:
            if ent.label_ != "GPE": # Geopolitical Entity
                continue
            text: str = ent.text
            if is_name_us_state(text):
                us_state: USState | None = convert_us_state_name_to_us_state(text)
                if us_state is not None:
                    us_state_counter[us_state] += 1
                continue
            if is_iso_us_state(text):
                us_state: USState | None = convert_us_state_iso_to_us_state(text)
                if us_state is not None:
                    us_state_counter[us_state] += 1
                continue
            location_counter[text] += 1

        most_common_us_state: USState | None = us_state_counter.most_common(1)[0][0]
        top_5_locations_raw: list[tuple[str, int]] = location_counter.most_common(5)
        top_5_locations: list[str] = []
        for location, _ in top_5_locations_raw:
            top_5_locations.append(location)

        return NLPLocationMatchResponse(
            us_state=most_common_us_state,
            locations=top_5_locations
        )



