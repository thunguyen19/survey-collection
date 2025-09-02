import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    FeedbackResponseType,
    FeedbackResponseTypeCreate,
    FeedbackResponseTypePublic,
    FeedbackResponseTypesPublic,
    FeedbackResponseTypeUpdate,
    Message,
    UserType,
)

router = APIRouter(prefix="/feedback-response-types", tags=["feedback-response-types"])


@router.get("/", response_model=FeedbackResponseTypesPublic)
def read_feedback_response_types(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve feedback response types. All users can view available response types.
    """
    count_statement = select(func.count()).select_from(FeedbackResponseType).where(
        FeedbackResponseType.active == True
    )
    count = session.exec(count_statement).one()

    statement = (
        select(FeedbackResponseType)
        .where(FeedbackResponseType.active == True)
        .offset(skip)
        .limit(limit)
    )
    response_types = session.exec(statement).all()

    return FeedbackResponseTypesPublic(data=response_types, count=count)


@router.get("/all", response_model=FeedbackResponseTypesPublic)
def read_all_feedback_response_types(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> Any:
    """
    Retrieve all feedback response types (including inactive ones if requested).
    Only admins can see inactive response types.
    """
    if include_inactive and not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only admins can view inactive response types"
        )

    base_query = select(FeedbackResponseType)
    count_query = select(func.count()).select_from(FeedbackResponseType)
    
    if not include_inactive:
        base_query = base_query.where(FeedbackResponseType.active == True)
        count_query = count_query.where(FeedbackResponseType.active == True)

    count = session.exec(count_query).one()
    response_types = session.exec(base_query.offset(skip).limit(limit)).all()

    return FeedbackResponseTypesPublic(data=response_types, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponseTypePublic,
)
def create_feedback_response_type(
    *, session: SessionDep, response_type_in: FeedbackResponseTypeCreate
) -> Any:
    """
    Create new feedback response type. Only superusers can create response types.
    """
    # Check if a response type with this name already exists
    existing_type = session.exec(
        select(FeedbackResponseType).where(
            FeedbackResponseType.type_name == response_type_in.type_name
        )
    ).first()
    
    if existing_type:
        raise HTTPException(
            status_code=400,
            detail="A response type with this name already exists"
        )
    
    response_type = FeedbackResponseType.model_validate(response_type_in)
    session.add(response_type)
    session.commit()
    session.refresh(response_type)
    return response_type


@router.get("/{response_type_id}", response_model=FeedbackResponseTypePublic)
def read_feedback_response_type(
    response_type_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get feedback response type by ID.
    """
    response_type = session.get(FeedbackResponseType, response_type_id)
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    # Only show inactive response types to admins
    if not response_type.active and not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    return response_type


@router.get("/by-name/{type_name}", response_model=FeedbackResponseTypePublic)
def read_feedback_response_type_by_name(
    type_name: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get feedback response type by name.
    """
    response_type = session.exec(
        select(FeedbackResponseType).where(
            FeedbackResponseType.type_name == type_name
        )
    ).first()
    
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    # Only show inactive response types to admins
    if not response_type.active and not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    return response_type


@router.get("/by-category/{category}", response_model=FeedbackResponseTypesPublic)
def read_feedback_response_types_by_category(
    category: str,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get feedback response types by category.
    """
    count_statement = select(func.count()).select_from(FeedbackResponseType).where(
        FeedbackResponseType.type_category == category,
        FeedbackResponseType.active == True
    )
    count = session.exec(count_statement).one()

    statement = (
        select(FeedbackResponseType)
        .where(
            FeedbackResponseType.type_category == category,
            FeedbackResponseType.active == True
        )
        .offset(skip)
        .limit(limit)
    )
    response_types = session.exec(statement).all()

    return FeedbackResponseTypesPublic(data=response_types, count=count)


@router.patch(
    "/{response_type_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponseTypePublic,
)
def update_feedback_response_type(
    *,
    session: SessionDep,
    response_type_id: uuid.UUID,
    response_type_in: FeedbackResponseTypeUpdate,
) -> Any:
    """
    Update a feedback response type. Only superusers can update response types.
    """
    response_type = session.get(FeedbackResponseType, response_type_id)
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    # Check if updating type_name would create a duplicate
    if response_type_in.type_name and response_type_in.type_name != response_type.type_name:
        existing_type = session.exec(
            select(FeedbackResponseType).where(
                FeedbackResponseType.type_name == response_type_in.type_name
            )
        ).first()
        
        if existing_type:
            raise HTTPException(
                status_code=400,
                detail="A response type with this name already exists"
            )
    
    update_dict = response_type_in.model_dump(exclude_unset=True)
    response_type.sqlmodel_update(update_dict)
    session.add(response_type)
    session.commit()
    session.refresh(response_type)
    return response_type


@router.delete(
    "/{response_type_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_feedback_response_type(
    session: SessionDep, response_type_id: uuid.UUID
) -> Message:
    """
    Delete a feedback response type. Only superusers can delete response types.
    This will fail if there are existing feedback responses using this type.
    """
    response_type = session.get(FeedbackResponseType, response_type_id)
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    # Check if there are existing responses using this type
    from app.models import FeedbackResponse
    existing_responses = session.exec(
        select(FeedbackResponse).where(
            FeedbackResponse.response_type_id == response_type_id
        ).limit(1)
    ).first()
    
    if existing_responses:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete response type that is being used by existing feedback responses"
        )
    
    session.delete(response_type)
    session.commit()
    return Message(message="Feedback response type deleted successfully")


@router.patch(
    "/{response_type_id}/activate",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponseTypePublic,
)
def activate_feedback_response_type(
    response_type_id: uuid.UUID, session: SessionDep
) -> Any:
    """
    Activate a feedback response type.
    """
    response_type = session.get(FeedbackResponseType, response_type_id)
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    response_type.active = True
    session.add(response_type)
    session.commit()
    session.refresh(response_type)
    return response_type


@router.patch(
    "/{response_type_id}/deactivate",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponseTypePublic,
)
def deactivate_feedback_response_type(
    response_type_id: uuid.UUID, session: SessionDep
) -> Any:
    """
    Deactivate a feedback response type.
    """
    response_type = session.get(FeedbackResponseType, response_type_id)
    if not response_type:
        raise HTTPException(status_code=404, detail="Feedback response type not found")
    
    response_type.active = False
    session.add(response_type)
    session.commit()
    session.refresh(response_type)
    return response_type
