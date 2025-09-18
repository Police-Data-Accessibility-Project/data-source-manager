from collections import defaultdict

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.subsets.nlp_responses import \
    NLPResponseSubsets
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion


def filter_valid_and_invalid_nlp_responses(
    mappings: list[URLToNLPResponseMapping]
) -> NLPResponseSubsets:
    valid: list[URLToNLPResponseMapping] = []
    invalid: list[URLToNLPResponseMapping] = []
    for mapping in mappings:
        nlp_response: NLPLocationMatchResponse = mapping.nlp_response
        if nlp_response.valid:
            valid.append(mapping)
        else:
            invalid.append(mapping)
    return NLPResponseSubsets(
        valid=valid,
        invalid=invalid,
    )

def filter_top_n_suggestions(
    subtask_data_list: list[AutoLocationIDSubtaskData],
    n: int = 5
) -> None:
    """Filters out all but the top N suggestions for each URL.

    Modifies:
        - AutoLocationIDSubtaskData.suggestions
    """
    for subtask_data in subtask_data_list:
        # Eliminate location ID duplicates;
        location_to_suggestions: dict[int, list[LocationSuggestion]] = defaultdict(list)
        for suggestion in subtask_data.suggestions:
            location_to_suggestions[suggestion.location_id].append(suggestion)

        # in the case of a tie, keep the suggestion with the highest confidence
        deduped_suggestions: list[LocationSuggestion] = []
        for location_suggestions in location_to_suggestions.values():
            location_suggestions.sort(
                key=lambda x: x.confidence,
                reverse=True  # Descending order
            )
            deduped_suggestions.append(location_suggestions[0])

        # Sort suggestions by confidence and keep top N
        suggestions_sorted: list[LocationSuggestion] = sorted(
            deduped_suggestions,
            key=lambda x: x.confidence,
            reverse=True  # Descending order
        )
        subtask_data.suggestions = suggestions_sorted[:n]
