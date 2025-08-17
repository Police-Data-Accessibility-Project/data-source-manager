from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping
from src.core.tasks.scheduled.impl.internet_archives.probe.models.subset import IAURLMappingSubsets


def filter_into_subsets(
    ia_mappings: list[InternetArchivesURLMapping]
) -> IAURLMappingSubsets:
    subsets = IAURLMappingSubsets()
    for ia_mapping in ia_mappings:
        if ia_mapping.has_error:
            subsets.error.append(ia_mapping)

        if ia_mapping.has_metadata:
            subsets.has_metadata.append(ia_mapping)

    return subsets
