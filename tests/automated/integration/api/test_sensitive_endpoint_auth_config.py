from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_proposal_mutation_routes_require_admin_auth():
    proposals_routes = (
        ROOT / "src" / "api" / "endpoints" / "proposals" / "routes.py"
    ).read_text()

    assert '"/agencies/{proposed_agency_id}/locations/{location_id}",\n    dependencies=[Depends(get_admin_access_info)],' in proposals_routes
    assert '"/agencies/{proposed_agency_id}",\n    dependencies=[Depends(get_admin_access_info)],' in proposals_routes


def test_submit_data_source_requires_authenticated_user():
    submit_routes = (
        ROOT / "src" / "api" / "endpoints" / "submit" / "routes.py"
    ).read_text()

    assert (
        '"/data-source",\n'
        "    response_model=SubmitDataSourceURLProposalResponse,\n"
        "    responses={\n"
        "        409: {\n"
        '            "model": SubmitDataSourceURLDuplicateSubmissionResponse\n'
        "        }\n"
        "    },\n"
        "    dependencies=[Depends(get_standard_user_access_info)]"
    ) in submit_routes
