import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    FeedbackResponse,
    FeedbackResponseCreate,
    FeedbackResponsePublic,
    FeedbackResponsesPublic,
    FeedbackResponseUpdate,
    FeedbackSession,
    Message,
    SurveyTemplate,
)

router = APIRouter(prefix="/feedback-responses", tags=["feedback-responses"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponsesPublic,
)
def read_feedback_responses(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve feedback responses for the current user's organization. Admin access only for MVP.
    """
    base_query = (
        select(FeedbackResponse)
        .join(FeedbackResponse.session)
        .join(FeedbackSession.survey_template)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
    )
    count_query = (
        select(func.count())
        .select_from(FeedbackResponse)
        .join(FeedbackResponse.session)
        .join(FeedbackSession.survey_template)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
    )
    
    count = session.exec(count_query).one()
    responses = session.exec(base_query.offset(skip).limit(limit)).all()
    
    return FeedbackResponsesPublic(data=responses, count=count)


@router.post("/", response_model=FeedbackResponsePublic)
def create_feedback_response(
    *, session: SessionDep, response_in: FeedbackResponseCreate
) -> Any:
    """
    Create new feedback response. This endpoint allows public access for survey respondents.
    """
    # Verify feedback session exists
    feedback_session = session.get(FeedbackSession, response_in.session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    # Check if session is expired
    from datetime import datetime
    if (feedback_session.expired_at and 
        feedback_session.expired_at < datetime.utcnow()):
        raise HTTPException(status_code=410, detail="Feedback session has expired")
    
    # Verify response type exists
    from app.models import FeedbackResponseType
    response_type = session.get(FeedbackResponseType, response_in.response_type_id)
    if not response_type or not response_type.active:
        raise HTTPException(status_code=404, detail="Response type not found or inactive")
    
    response = FeedbackResponse.model_validate(response_in)
    session.add(response)
    session.commit()
    session.refresh(response)
    return response


@router.post("/batch", response_model=List[FeedbackResponsePublic])
def create_feedback_responses_batch(
    *, session: SessionDep, responses_in: List[FeedbackResponseCreate]
) -> Any:
    """
    Create multiple feedback responses in a batch. Useful for submitting entire surveys.
    Public access for survey respondents.
    """
    if not responses_in:
        raise HTTPException(status_code=400, detail="No responses provided")
    
    # Verify all responses belong to the same session
    session_ids = {response.session_id for response in responses_in}
    if len(session_ids) > 1:
        raise HTTPException(
            status_code=400, detail="All responses must belong to the same feedback session"
        )
    
    session_id = next(iter(session_ids))
    
    # Verify feedback session exists and check expiration
    feedback_session = session.get(FeedbackSession, session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    from datetime import datetime
    if (feedback_session.expired_at and 
        feedback_session.expired_at < datetime.utcnow()):
        raise HTTPException(status_code=410, detail="Feedback session has expired")
    
    # Verify all response types exist and are active
    from app.models import FeedbackResponseType
    response_type_ids = {response.response_type_id for response in responses_in}
    response_types = session.exec(
        select(FeedbackResponseType).where(
            FeedbackResponseType.id.in_(response_type_ids)
        )
    ).all()
    
    active_type_ids = {rt.id for rt in response_types if rt.active}
    for response in responses_in:
        if response.response_type_id not in active_type_ids:
            raise HTTPException(
                status_code=404, 
                detail=f"Response type {response.response_type_id} not found or inactive"
            )
    
    # Create all responses
    created_responses = []
    for response_in in responses_in:
        response = FeedbackResponse.model_validate(response_in)
        session.add(response)
        created_responses.append(response)
    
    session.commit()
    
    # Refresh all responses
    for response in created_responses:
        session.refresh(response)
    
    return created_responses


@router.get(
    "/session/{session_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponsesPublic,
)
def read_responses_by_session(
    session_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all responses for a specific feedback session. Admin access only for MVP.
    """
    # Verify feedback session exists and belongs to user's organization
    feedback_session = session.get(FeedbackSession, session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Feedback session not found")
    
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    count_statement = select(func.count()).select_from(FeedbackResponse).where(
        FeedbackResponse.session_id == session_id
    )
    count = session.exec(count_statement).one()
    
    statement = (
        select(FeedbackResponse)
        .where(FeedbackResponse.session_id == session_id)
        .offset(skip)
        .limit(limit)
    )
    responses = session.exec(statement).all()
    
    return FeedbackResponsesPublic(data=responses, count=count)


@router.get(
    "/{response_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponsePublic,
)
def read_feedback_response(
    response_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get feedback response by ID. Admin access only for MVP.
    """
    response = session.get(FeedbackResponse, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Feedback response not found")
    
    # Check permissions via the feedback session
    feedback_session = session.get(FeedbackSession, response.session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Associated feedback session not found")
    
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return response


@router.patch(
    "/{response_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=FeedbackResponsePublic,
)
def update_feedback_response(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    response_id: uuid.UUID,
    response_in: FeedbackResponseUpdate,
) -> Any:
    """
    Update a feedback response. Admin access only for MVP.
    """
    response = session.get(FeedbackResponse, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Feedback response not found")
    
    # Check permissions via the feedback session
    feedback_session = session.get(FeedbackSession, response.session_id)
    if not feedback_session:
        raise HTTPException(status_code=404, detail="Associated feedback session not found")
    
    survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
    if not survey_template or survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = response_in.model_dump(exclude_unset=True)
    response.sqlmodel_update(update_dict)
    session.add(response)
    session.commit()
    session.refresh(response)
    return response


@router.delete(
    "/{response_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_feedback_response(
    session: SessionDep, current_user: CurrentUser, response_id: uuid.UUID
) -> Message:
    """
    Delete a feedback response. Admin access only for MVP.
    """
    response = session.get(FeedbackResponse, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Feedback response not found")
    
    # Check permissions via the feedback session
    feedback_session = session.get(FeedbackSession, response.session_id)
    if feedback_session:
        survey_template = session.get(SurveyTemplate, feedback_session.survey_template_id)
        if not survey_template or survey_template.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(response)
    session.commit()
    return Message(message="Feedback response deleted successfully")


@router.get(
    "/analytics/question/{question_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=dict,
)
def get_question_analytics(
    question_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get analytics for a specific question across all responses in the organization.
    Admin access only for MVP.
    """
    # Get all responses for this question in the organization
    responses = session.exec(
        select(FeedbackResponse)
        .join(FeedbackResponse.session)
        .join(FeedbackSession.survey_template)
        .where(
            FeedbackResponse.question_id == question_id,
            SurveyTemplate.organization_id == current_user.organization_id
        )
    ).all()
    
    if not responses:
        return {
            "question_id": question_id,
            "total_responses": 0,
            "response_summary": {}
        }
    
    # Analyze responses
    response_values = [r.response_value for r in responses if r.response_value]
    response_texts = [r.response_text for r in responses if r.response_text]
    
    return {
        "question_id": question_id,
        "total_responses": len(responses),
        "response_summary": {
            "value_responses": len(response_values),
            "text_responses": len(response_texts),
            "average_response_time": sum(r.response_time_seconds for r in responses if r.response_time_seconds) / len([r for r in responses if r.response_time_seconds]) if any(r.response_time_seconds for r in responses) else None,
        },
        "sample_responses": response_texts[:5] if response_texts else [],
    }
