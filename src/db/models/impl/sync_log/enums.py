from enum import Enum


class ResourceType(Enum):
    AGENCY = 'agency'
    DATA_SOURCE = 'data_source'
    META_URL = 'meta_url'

class SyncType(Enum):
    ADD = 'add'
    UPDATE = 'update'
    DELETE = 'delete'