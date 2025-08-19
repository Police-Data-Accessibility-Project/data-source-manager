from src.core.tasks.scheduled.impl.internet_archives.save.models.mapping import URLInternetArchivesSaveResponseMapping
from src.core.tasks.scheduled.impl.internet_archives.save.models.subset import IASaveURLMappingSubsets


def filter_save_responses(
    resp_mappings: list[URLInternetArchivesSaveResponseMapping]
) -> IASaveURLMappingSubsets:
    subsets = IASaveURLMappingSubsets()
    for resp_mapping in resp_mappings:
        if resp_mapping.response.has_error:
            subsets.error.append(resp_mapping.response)
        else:
            subsets.success.append(resp_mapping.response)
    return subsets