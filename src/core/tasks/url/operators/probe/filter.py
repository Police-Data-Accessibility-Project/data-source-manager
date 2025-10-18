from src.core.tasks.url.operators.probe.models.subsets import RedirectTDOSubsets
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.util.models.full_url import FullURL


def filter_non_redirect_tdos(tdos: list[URLProbeTDO]) -> list[URLProbeTDO]:
    return [tdo for tdo in tdos if not tdo.response.is_redirect]

def filter_redirect_tdos(tdos: list[URLProbeTDO]) -> list[URLProbeTDO]:
    return [tdo for tdo in tdos if tdo.response.is_redirect]

def filter_functionally_equivalent_urls(tdos: list[URLProbeTDO]) -> RedirectTDOSubsets:
    true_redirects: list[URLProbeTDO] = []
    functional_equivalents: list[URLProbeTDO] = []
    for tdo in tdos:
        og_url: FullURL = tdo.url_mapping.full_url
        response: URLProbeRedirectResponsePair = tdo.response.response
        redirect_url: FullURL = response.destination.url

        if og_url.id_form != redirect_url.id_form:
            true_redirects.append(tdo)
        # Otherwise, they are functional equivalents.
        else:
            functional_equivalents.append(tdo)

    return RedirectTDOSubsets(
        true_redirects=true_redirects,
        functional_equivalents=functional_equivalents
    )