from collections import Counter

import spacy
from spacy import Language
from spacy.tokens import Doc

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.check import \
    is_name_us_state, is_iso_us_state
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.convert import \
    convert_us_state_name_to_us_state, convert_us_state_iso_to_us_state
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.enums import \
    SpacyModelType
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.extract import \
    extract_most_common_us_state, extract_top_n_locations
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.us_state import \
    USState


class NLPProcessor:

    def __init__(
        self,
        model_type: SpacyModelType = SpacyModelType.EN_CORE_WEB_SM
    ):
        self._model_type: SpacyModelType = model_type
        self._model: Language | None = None

    def lazy_load_model(self) -> Language:
        if self._model is None:
            self._model = spacy.load(self._model_type.value, disable=['parser'])
        return self._model


    def parse_for_locations(self, html: str) -> NLPLocationMatchResponse:
        model: Language = self.lazy_load_model()
        doc: Doc = model(html)
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

        # Get most common US State if exists
        most_common_us_state: USState | None = extract_most_common_us_state(us_state_counter)

        top_n_locations: list[str] = extract_top_n_locations(location_counter)

        return NLPLocationMatchResponse(
            us_state=most_common_us_state,
            locations=top_n_locations
        )



