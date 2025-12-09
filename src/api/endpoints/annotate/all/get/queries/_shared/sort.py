from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel


def sort_suggestions(
    suggestions: list[SuggestionModel]
) -> list[SuggestionModel]:
    """
    Sort according to the following criterion:
        - Each user suggestion is a point
        - The robo suggestion is a point * (confidence /100)
        - Sort in descending order of points
    """
    return sorted(suggestions, key=lambda s: s.score, reverse=True)