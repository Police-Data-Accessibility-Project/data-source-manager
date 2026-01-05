import uuid
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from src.api.dependencies import get_async_core
from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.get.queries.agency.core import GetAgencySuggestionsQueryBuilder
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.all.post.query import AddAllAnnotationsToURLQueryBuilder
from src.api.endpoints.annotate.anonymous.get.query import GetNextURLForAnonymousAnnotationQueryBuilder
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.api.endpoints.annotate.anonymous.post.query import AddAnonymousAnnotationsToURLQueryBuilder
from src.api.endpoints.annotate.migrate.query import MigrateAnonymousAnnotationsQueryBuilder
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore
from src.db.queries.implementations.anonymous_session import MakeAnonymousSessionQueryBuilder
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_admin_access_info, get_standard_user_access_info

annotate_router = APIRouter(
    prefix="/annotate",
    tags=["annotate"],
    responses={404: {"description": "Not found"}},
)

batch_query = Query(
    description="The batch id of the next URL to get. "
                "If not specified, defaults to first qualifying URL",
    default=None
)
url_id_query = Query(
    description="The URL id to annotate. " +
                "If not specified, defaults to first qualifying URL",
    default=None
)


@annotate_router.get("/anonymous")
async def get_next_url_for_all_annotations_anonymous(
    async_core: AsyncCore = Depends(get_async_core),
    session_id: UUID | None = Query(description="The session id of the anonymous user.", default=None),
    offset: int | None = Query(
        description="Offset for annotation",
        default=None
    )
) -> GetNextURLForAnonymousAnnotationResponse:
    # If session_id is not provided, generate new UUID
    if session_id is None:
        session_id: uuid.UUID = await async_core.adb_client.run_query_builder(
            MakeAnonymousSessionQueryBuilder()
        )

    return await async_core.adb_client.run_query_builder(
        GetNextURLForAnonymousAnnotationQueryBuilder(
            session_id=session_id,
            offset=offset
        )
    )


@annotate_router.post("/anonymous/{url_id}")
async def annotate_url_for_all_annotations(
    url_id: int,
    all_annotation_post_info: AllAnnotationPostInfo,
    async_core: AsyncCore = Depends(get_async_core),
    session_id: UUID = Query(description="The session id of the anonymous user"),
    get_next_url: bool = Query(
        description="Get next URL after submitting this URL",
        default=True
    )
) -> GetNextURLForAnonymousAnnotationResponse:
    await async_core.adb_client.run_query_builder(
        AddAnonymousAnnotationsToURLQueryBuilder(
            url_id=url_id,
            post_info=all_annotation_post_info,
            session_id=session_id
        )
    )
    if not get_next_url:
        return GetNextURLForAnonymousAnnotationResponse(
            next_annotation=None,
            session_id=session_id
        )

    return await async_core.adb_client.run_query_builder(
        GetNextURLForAnonymousAnnotationQueryBuilder(
            session_id=session_id
        )
    )



@annotate_router.get("/all")
async def get_next_url_for_all_annotations(
        access_info: AccessInfo = Depends(get_standard_user_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: int | None = batch_query,
        anno_url_id: int | None = url_id_query,
        offset: int | None = Query(
            description="Offset for annotation",
            default=None
        )
) -> GetNextURLForAllAnnotationResponse:
    if anno_url_id is not None and offset is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="anno_url_id and offset query arguments cannot both be defined"
        )
    return await async_core.adb_client.get_next_url_for_all_annotations(
        batch_id=batch_id,
        user_id=access_info.user_id,
        url_id=anno_url_id
    )

@annotate_router.post("/all/{url_id}")
async def annotate_url_for_all_annotations(
        url_id: int,
        all_annotation_post_info: AllAnnotationPostInfo,
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_standard_user_access_info),
        batch_id: int | None = batch_query,
        anno_url_id: int | None = url_id_query,
        get_next_url: bool = Query(
            description="Get next URL after submitting this URL",
            default=True
        )
) -> GetNextURLForAllAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.adb_client.run_query_builder(
            AddAllAnnotationsToURLQueryBuilder(
                user_id=access_info.user_id,
                url_id=url_id,
                post_info=all_annotation_post_info
            )
        )

    if not get_next_url:
        return GetNextURLForAllAnnotationResponse(
            next_annotation=None
        )

    return await async_core.adb_client.get_next_url_for_all_annotations(
        batch_id=batch_id,
        user_id=access_info.user_id,
        url_id=anno_url_id
    )

@annotate_router.post('/migrate')
async def migrate_annotations_to_user(
    async_core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_standard_user_access_info),
    session_id: UUID = Query(description="The session id of the anonymous user")
) -> MessageResponse:
    """Migrate annotations from an anonymous session to a user's account."""
    await async_core.adb_client.run_query_builder(
        MigrateAnonymousAnnotationsQueryBuilder(
            session_id=session_id,
            user_id=access_info.user_id
        )
    )
    return MessageResponse(
        message="Annotations migrated successfully."
    )

@annotate_router.get("/suggestions/agencies/{url_id}")
async def get_agency_suggestions(
    url_id: int,
    async_core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_admin_access_info),
    location_id: int | None = Query(default=None)
) -> AgencyAnnotationResponseOuterInfo:
    return await async_core.adb_client.run_query_builder(
        GetAgencySuggestionsQueryBuilder(
            url_id=url_id,
            location_id=location_id
        )
    )

