import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    FeedbackSession,
    FeedbackSessionCreate,
    FeedbackSessionPublic,
    FeedbackSessionsPublic,
    FeedbackSessionUpdate,
    FeedbackSessionStatus,
    Message,
    SurveyTemplate,
    UserType,
)

router = APIRouter(prefix="/feedback-sessions", tags=["feedback-sessions"])


@router.get("/", response_model=FeedbackSessionsPublic)
def read_feedback_sessions(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve feedback sessions for the current user's organization.
    Admins and providers can view sessions.
    """
    # Only allow admins and providers to view sessions
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view feedback sessions"
        )
    base_query = (
        select(FeedbackSession)
        .join(FeedbackSession.survey_template)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
    )
    count_query = (
        select(func.count())
        .select_from(FeedbackSession)
        .join(FeedbackSession.survey_template)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
    )
    
    count = session.exec(count_query).one()
    feedback_sessions = session.exec(base_query.offset(skip).limit(limit)).all()
    
    return FeedbackSessionsPublic(data=feedback_sessions, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackSessionPublic,
)
def create_feedback_session(
    *, session: SessionDep, current_user: CurrentUser, feedback_session_in: FeedbackSessionCreate
) -> Any:
    """
    Create new feedback session. Admin access only for MVP.
    """
    # Verify survey template exists and belongs to the same organization
    survey_template = session.get(SurveyTemplate, feedback_session_in.survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Survey template not accessible")
    
    # Set expiration date if not provided (default: 7 days from now)
    session_data = feedback_session_in.model_dump()
    if not session_data.get("expired_at"):
        session_data["expired_at"] = datetime.utcnow() + timedelta(days=7)
    
    feedback_session = FeedbackSession.model_validate(session_data)
    session.add(feedback_session)
    session.commit()
    session.refresh(feedback_session)
    return feedback_session


@router.get("/by-token/{completion_token}", response_model=FeedbackSessionPublic)
def read_feedback_session_by_token(
    completion_token: uuid.UUID, session: SessionDep
) -> Any:
    """
    Get feedback session by completion token. This endpoint doesn't require authentication
    as it's used by survey respondents to access surveys via email/SMS links.
    """
    feedback_session = session.exec(
        select(FeedbackSession).where(
            FeedbackSession.completion_token == completion_token
        )
    ).first()
    
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session is expired
    if (feedback_session.expired_at and 
        feedback_session.expired_at < datetime.utcnow()):
        raise HTTPException(status_code=410, detail="Feedback session has expired")
    
    return feedback_session


@router.get("/{feedback_session_id}", response_model=FeedbackSessionPublic)
def read_feedback_session(
    feedback_session_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get feedback session by ID. Admins and providers can view sessions.
    """
    # Only allow admins and providers to view sessions
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view feedback sessions"
        )
    feedback_session = session.get(FeedbackSession, feedback_session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session belongs to user's organization
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return feedback_session


@router.patch(
    "/{feedback_session_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackSessionPublic,
)
def update_feedback_session(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    feedback_session_id: uuid.UUID,
    feedback_session_in: FeedbackSessionUpdate,
) -> Any:
    """
    Update a feedback session. Admin access only for MVP.
    """
    feedback_session = session.get(FeedbackSession, feedback_session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session belongs to user's organization
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = feedback_session_in.model_dump(exclude_unset=True)
    feedback_session.sqlmodel_update(update_dict)
    session.add(feedback_session)
    session.commit()
    session.refresh(feedback_session)
    return feedback_session


@router.patch("/by-token/{completion_token}", response_model=FeedbackSessionPublic)
def update_feedback_session_by_token(
    *,
    session: SessionDep,
    completion_token: uuid.UUID,
    feedback_session_in: FeedbackSessionUpdate,
    request: Request,
) -> Any:
    """
    Update a feedback session by completion token. This is used when survey respondents
    interact with surveys via email/SMS links.
    """
    feedback_session = session.exec(
        select(FeedbackSession).where(
            FeedbackSession.completion_token == completion_token
        )
    ).first()
    
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session is expired
    if (feedback_session.expired_at and 
        feedback_session.expired_at < datetime.utcnow()):
        raise HTTPException(status_code=410, detail="Feedback session has expired")
    
    # Automatically capture IP address and user agent
    update_dict = feedback_session_in.model_dump(exclude_unset=True)
    update_dict["ip_address"] = request.client.host if request.client else None
    update_dict["user_agent"] = request.headers.get("user-agent")
    
    # Set first_response_at if this is the first response
    if (feedback_session.status == FeedbackSessionStatus.INITIATED and 
        not feedback_session.first_response_at):
        update_dict["first_response_at"] = datetime.utcnow()
        update_dict["status"] = FeedbackSessionStatus.IN_PROGRESS
    
    feedback_session.sqlmodel_update(update_dict)
    session.add(feedback_session)
    session.commit()
    session.refresh(feedback_session)
    return feedback_session


@router.delete(
    "/{feedback_session_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_feedback_session(
    session: SessionDep, current_user: CurrentUser, feedback_session_id: uuid.UUID
) -> Message:
    """
    Delete a feedback session. Admin access only for MVP.
    """
    feedback_session = session.get(FeedbackSession, feedback_session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session belongs to user's organization
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(feedback_session)
    session.commit()
    return Message(message="Feedback session deleted successfully")


@router.patch(
    "/{feedback_session_id}/complete",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackSessionPublic,
)
def complete_feedback_session(
    feedback_session_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Mark a feedback session as completed. Admin access only for MVP.
    """
    feedback_session = session.get(FeedbackSession, feedback_session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session belongs to user's organization
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    feedback_session.status = FeedbackSessionStatus.COMPLETED
    feedback_session.completed_at = datetime.utcnow()
    
    # Calculate completion time if we have first_response_at
    if feedback_session.first_response_at:
        completion_time = datetime.utcnow() - feedback_session.first_response_at
        feedback_session.completion_time_seconds = int(completion_time.total_seconds())
    
    session.add(feedback_session)
    session.commit()
    session.refresh(feedback_session)
    return feedback_session


@router.patch("/by-token/{completion_token}/complete", response_model=FeedbackSessionPublic)
def complete_feedback_session_by_token(
    completion_token: uuid.UUID, session: SessionDep, request: Request
) -> Any:
    """
    Mark a feedback session as completed by completion token.
    This is used when survey respondents complete surveys via email/SMS links.
    """
    feedback_session = session.exec(
        select(FeedbackSession).where(
            FeedbackSession.completion_token == completion_token
        )
    ).first()
    
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session is expired
    if (feedback_session.expired_at and 
        feedback_session.expired_at < datetime.utcnow()):
        raise HTTPException(status_code=410, detail="Feedback session has expired")
    
    feedback_session.status = FeedbackSessionStatus.COMPLETED
    feedback_session.completed_at = datetime.utcnow()
    feedback_session.ip_address = request.client.host if request.client else None
    feedback_session.user_agent = request.headers.get("user-agent")
    
    # Calculate completion time if we have first_response_at
    if feedback_session.first_response_at:
        completion_time = datetime.utcnow() - feedback_session.first_response_at
        feedback_session.completion_time_seconds = int(completion_time.total_seconds())
    
    session.add(feedback_session)
    session.commit()
    session.refresh(feedback_session)
    return feedback_session


@router.get("/stats/organization", response_model=dict)
def get_organization_feedback_stats(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get feedback session statistics for the current user's organization.
    Admins and providers can view statistics.
    """
    # Only allow admins and providers to view statistics
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view organization statistics"
        )
    # Get sessions for the organization
    base_query = (
        select(FeedbackSession)
        .join(FeedbackSession.survey_template)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
    )
    
    total_sessions = session.exec(select(func.count()).select_from(base_query.subquery())).one()
    
    completed_sessions = session.exec(
        select(func.count())
        .select_from(base_query.where(FeedbackSession.status == FeedbackSessionStatus.COMPLETED).subquery())
    ).one()
    
    in_progress_sessions = session.exec(
        select(func.count())
        .select_from(base_query.where(FeedbackSession.status == FeedbackSessionStatus.IN_PROGRESS).subquery())
    ).one()
    
    expired_sessions = session.exec(
        select(func.count())
        .select_from(base_query.where(FeedbackSession.status == FeedbackSessionStatus.EXPIRED).subquery())
    ).one()
    
    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "in_progress_sessions": in_progress_sessions,
        "expired_sessions": expired_sessions,
        "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
    }
