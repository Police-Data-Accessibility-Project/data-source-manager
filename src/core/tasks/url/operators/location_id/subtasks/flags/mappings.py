from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType

SUBTASK_TO_ENV_FLAG: dict[LocationIDSubtaskType, str] = {
    LocationIDSubtaskType.NLP_LOCATION_FREQUENCY: "LOCATION_ID_NLP_LOCATION_MATCH_FLAG",
    LocationIDSubtaskType.BATCH_LINK: "LOCATION_ID_BATCH_LINK_FLAG",
}