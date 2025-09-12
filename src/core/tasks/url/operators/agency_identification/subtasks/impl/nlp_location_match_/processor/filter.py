from collections import defaultdict

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.subsets.nlp_responses import \
    NLPResponseSubsets
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion


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
    subtask_data_list: list[AutoAgencyIDSubtaskData],
    n: int = 5
) -> None:
    """Filters out all but the top N suggestions for each URL.

    Modifies:
        - AutoAgencyIDSubtaskData.suggestions
    """
    for subtask_data in subtask_data_list:
        # Eliminate agency ID duplicates;
        agency_to_suggestions: dict[int, list[AgencySuggestion]] = defaultdict(list)
        for suggestion in subtask_data.suggestions:
            agency_to_suggestions[suggestion.agency_id].append(suggestion)

        # in the case of a tie, keep the suggestion with the highest confidence
        deduped_suggestions: list[AgencySuggestion] = []
        for agency_suggestions in agency_to_suggestions.values():
            agency_suggestions.sort(
                key=lambda x: x.confidence,
                reverse=True  # Descending order
            )
            deduped_suggestions.append(agency_suggestions[0])

        # Sort suggestions by confidence and keep top N
        suggestions_sorted: list[AgencySuggestion] = sorted(
            deduped_suggestions,
            key=lambda x: x.confidence,
            reverse=True  # Descending order
        )
        subtask_data.suggestions = suggestions_sorted[:n]
