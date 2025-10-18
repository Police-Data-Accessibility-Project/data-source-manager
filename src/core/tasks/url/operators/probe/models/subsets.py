from pydantic import BaseModel

from src.core.tasks.url.operators.probe.tdo import URLProbeTDO


class RedirectTDOSubsets(BaseModel):
    true_redirects: list[URLProbeTDO]
    functional_equivalents: list[URLProbeTDO]
