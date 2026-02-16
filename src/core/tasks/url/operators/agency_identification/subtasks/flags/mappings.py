from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType

SUBTASK_TO_ENV_FLAG: dict[AutoAgencyIDSubtaskType, str] = {
    AutoAgencyIDSubtaskType.HOMEPAGE_MATCH: "AGENCY_ID_HOMEPAGE_MATCH_FLAG",
    AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH: "AGENCY_ID_NLP_LOCATION_MATCH_FLAG",
    AutoAgencyIDSubtaskType.CKAN: "AGENCY_ID_CKAN_FLAG",
    AutoAgencyIDSubtaskType.MUCKROCK: "AGENCY_ID_MUCKROCK_FLAG",
    AutoAgencyIDSubtaskType.BATCH_LINK: "AGENCY_ID_BATCH_LINK_FLAG"
}