from sqlalchemy import select, func, and_

from src.api.endpoints.contributions.user.queries.annotated_and_validated import AnnotatedAndValidatedCTEContainer
from src.api.endpoints.contributions.user.queries.templates.agreement import AgreementCTEContainer
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser


def get_record_type_agreement_cte_container(
    inner_cte: AnnotatedAndValidatedCTEContainer
) -> AgreementCTEContainer:

    count_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            AnnotationRecordTypeUser,
            AnnotationRecordTypeUser.url_id == inner_cte.url_id
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("record_type_count_total")
    )

    agreed_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            AnnotationRecordTypeUser,
            AnnotationRecordTypeUser.url_id == inner_cte.url_id
        )
        .join(
            URLRecordType,
            and_(
                URLRecordType.url_id == inner_cte.url_id,
                URLRecordType.record_type == AnnotationRecordTypeUser.record_type
            )
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("record_type_count_agreed")
    )

    return AgreementCTEContainer(
        count_cte=count_cte,
        agreed_cte=agreed_cte,
        name="record_type"
    )