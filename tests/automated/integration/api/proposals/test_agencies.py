import pytest

from src.api.endpoints.proposals.agencies.approve.response import ProposalAgencyApproveResponse
from src.api.endpoints.proposals.agencies.get.response import ProposalAgencyGetOuterResponse
from src.api.endpoints.proposals.agencies.reject.request import ProposalAgencyRejectRequestModel
from src.api.endpoints.proposals.agencies.reject.response import ProposalAgencyRejectResponse
from src.api.endpoints.submit.agency.enums import AgencyProposalRequestStatus
from src.api.endpoints.submit.agency.request import SubmitAgencyRequestModel
from src.api.endpoints.submit.agency.response import SubmitAgencyProposalResponse
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.automated.integration.conftest import MOCK_USER_ID
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_agencies(
    api_test_helper: APITestHelper,
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo
):
    request = SubmitAgencyRequestModel(
        name="test_agency",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.LOCAL,
        location_ids=[
            allegheny_county.location_id,
            pittsburgh_locality.location_id
        ]
    )

    rv: RequestValidator = api_test_helper.request_validator
    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()
    # Add pending agency
    submit_response_success: SubmitAgencyProposalResponse = rv.post_v3(
        "/submit/agency",
        expected_model=SubmitAgencyProposalResponse,
        json=request.model_dump(mode="json")
    )
    assert submit_response_success.status == AgencyProposalRequestStatus.SUCCESS
    proposal_id: int = submit_response_success.proposal_id

    # Try to submit duplicate agency and confirm it fails
    submit_response_proposal_duplicate: SubmitAgencyProposalResponse = rv.post_v3(
        "/submit/agency",
        expected_model=SubmitAgencyProposalResponse,
        json=request.model_dump(mode="json")
    )
    assert submit_response_proposal_duplicate.status == AgencyProposalRequestStatus.PROPOSAL_DUPLICATE
    assert submit_response_proposal_duplicate.proposal_id is None
    assert submit_response_proposal_duplicate.details == "An agency with the same properties is already in the proposal queue."

    # Call GET endpoint
    get_response_1: ProposalAgencyGetOuterResponse = rv.get_v3(
        "/proposal/agencies",
        expected_model=ProposalAgencyGetOuterResponse
    )
    # Confirm agency is in response
    assert len(get_response_1.results) == 1
    proposal = get_response_1.results[0]
    assert proposal.id == proposal_id
    assert proposal.name == request.name
    assert proposal.proposing_user_id == MOCK_USER_ID
    assert proposal.agency_type == request.agency_type
    assert proposal.jurisdiction_type == request.jurisdiction_type
    assert [loc.location_id for loc in proposal.locations] == request.location_ids
    assert proposal.created_at is not None

    # Call APPROVE endpoint
    approve_response: ProposalAgencyApproveResponse = rv.post_v3(
        f"/proposal/agencies/{proposal_id}/approve",
        expected_model=ProposalAgencyApproveResponse
    )
    assert approve_response.message == "Proposed agency approved."
    assert approve_response.success
    assert approve_response.agency_id is not None
    agency_id: int = approve_response.agency_id

    # Check agency is added
    agencies: list[Agency] = await adb_client.get_all(Agency)
    assert len(agencies) == 1
    agency = agencies[0]
    assert agency.name == request.name
    assert agency.agency_type == request.agency_type
    assert agency.jurisdiction_type == request.jurisdiction_type

    links: list[LinkAgencyLocation] = await adb_client.get_all(LinkAgencyLocation)
    assert len(links) == 2
    assert {link.agency_id for link in links} == {agency.id}
    assert {link.location_id for link in links} == set(request.location_ids)

    # Confirm agency is no longer in proposal queue
    get_response_2: ProposalAgencyGetOuterResponse = rv.get_v3(
        "/proposal/agencies",
        expected_model=ProposalAgencyGetOuterResponse
    )
    # Confirm agency is in response
    assert len(get_response_2.results) == 0

    # Try to submit agency again and confirm it fails
    submit_response_accepted_duplicate: SubmitAgencyProposalResponse = rv.post_v3(
        "/submit/agency",
        expected_model=SubmitAgencyProposalResponse,
        json=request.model_dump(mode="json")
    )
    assert submit_response_accepted_duplicate.status == AgencyProposalRequestStatus.ACCEPTED_DUPLICATE
    assert submit_response_accepted_duplicate.proposal_id is None
    assert submit_response_accepted_duplicate.details == "An agency with the same properties is already approved."

    # Submit Separate Agency and Reject It
    request_for_rejection = SubmitAgencyRequestModel(
        name="Rejectable Agency",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.FEDERAL,
        location_ids=[]
    )
    submit_response_for_rejection: SubmitAgencyProposalResponse = rv.post_v3(
        "/submit/agency",
        expected_model=SubmitAgencyProposalResponse,
        json=request_for_rejection.model_dump(mode="json")
    )
    assert submit_response_for_rejection.status == AgencyProposalRequestStatus.SUCCESS
    proposal_id_for_rejection: int = submit_response_for_rejection.proposal_id

    # Call REJECT endpoint
    reject_response: ProposalAgencyRejectResponse = rv.post_v3(
        f"/proposal/agencies/{proposal_id_for_rejection}/reject",
        expected_model=ProposalAgencyRejectResponse,
        json=ProposalAgencyRejectRequestModel(
            rejection_reason="Test rejection reason"
        ).model_dump(mode="json")
    )
    assert reject_response.success
    assert reject_response.message == "Proposed agency rejected."

    # Confirm does not appear in proposal queue OR final agency list
    agencies = await adb_client.get_all(Agency)
    assert len(agencies) == 1
    assert agencies[0].id == agency.id

    # Confirm cannot reject endpoint already approved
    failed_reject_response: ProposalAgencyRejectResponse = rv.post_v3(
        f"/proposal/agencies/{proposal_id}/reject",
        expected_model=ProposalAgencyRejectResponse,
        json=ProposalAgencyRejectRequestModel(
            rejection_reason="Test rejection reason"
        ).model_dump(mode="json")
    )
    assert not failed_reject_response.success
    assert failed_reject_response.message == "Proposed agency is not pending."

    # Confirm cannot approve endpoint already rejected
    failed_approve_response: ProposalAgencyApproveResponse = rv.post_v3(
        f"/proposal/agencies/{proposal_id_for_rejection}/approve",
        expected_model=ProposalAgencyApproveResponse
    )
    assert not failed_approve_response.success
    assert failed_approve_response.message == "Proposed agency is not pending."

