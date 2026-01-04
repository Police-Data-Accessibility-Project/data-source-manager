from src.core.tasks.url.operators.root_url.extract import extract_root_url
from src.core.tasks.url.operators.root_url.models.root_mapping import URLRootURLMapping
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.root_url.pydantic import FlagRootURLPydantic
from src.db.models.impl.link.urls_root_url.pydantic import LinkURLRootURLPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.util.url_mapper_.simple import SimpleURLMapper


def convert_to_flag_root_url_pydantic(url_ids: list[int]) -> list[FlagRootURLPydantic]:
    return [FlagRootURLPydantic(url_id=url_id) for url_id in url_ids]

def convert_to_url_root_url_mapping(url_mappings: list[SimpleURLMapping]) -> list[URLRootURLMapping]:
    return [
        URLRootURLMapping(
            url=mapping.url,
            root_url=extract_root_url(mapping.url)
        ) for mapping in url_mappings
    ]

def convert_to_url_insert_models(urls: list[str]) -> list[URLInsertModel]:
    return [
        URLInsertModel(
            url=url.rstrip('/'),
            source=URLSource.ROOT_URL,
            trailing_slash=url.endswith('/')
        ) for url in urls
    ]

def convert_to_root_url_links(
    root_db_mappings: list[SimpleURLMapping],
    branch_db_mappings: list[SimpleURLMapping],
    url_root_url_mappings: list[URLRootURLMapping]
) -> list[LinkURLRootURLPydantic]:
    root_mapper = SimpleURLMapper(root_db_mappings)
    branch_mapper = SimpleURLMapper(branch_db_mappings)
    results: list[LinkURLRootURLPydantic] = []

    for url_root_url_mapping in url_root_url_mappings:
        root_url_id = root_mapper.get_id(url_root_url_mapping.root_url)
        branch_url_id = branch_mapper.get_id(url_root_url_mapping.url)

        results.append(
            LinkURLRootURLPydantic(
                root_url_id=root_url_id,
                url_id=branch_url_id)
        )

    return results
