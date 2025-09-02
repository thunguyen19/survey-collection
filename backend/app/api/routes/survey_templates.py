import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Message,
    SurveyTemplate,
    SurveyTemplateCreate,
    SurveyTemplatePublic,
    SurveyTemplatesPublic,
    SurveyTemplateUpdate,
)

router = APIRouter(prefix="/survey-templates", tags=["survey-templates"])


@router.get("/", response_model=SurveyTemplatesPublic)
def read_survey_templates(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve survey templates for the current user's organization. 
    Admins and providers can view templates.
    """
    # Only allow admins and providers to view templates
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view survey templates"
        )
    count_statement = select(func.count()).select_from(SurveyTemplate).where(
        SurveyTemplate.organization_id == current_user.organization_id
    )
    count = session.exec(count_statement).one()

    statement = (
        select(SurveyTemplate)
        .where(SurveyTemplate.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
    )
    survey_templates = session.exec(statement).all()

    return SurveyTemplatesPublic(data=survey_templates, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SurveyTemplatePublic,
)
def create_survey_template(
    *, session: SessionDep, current_user: CurrentUser, survey_template_in: SurveyTemplateCreate
) -> Any:
    """
    Create new survey template. Admin access only for MVP.
    """
    
    # Ensure the survey template is created for the user's organization
    # Always override organization_id and created_by with current user's info
    survey_template_data = survey_template_in.model_dump()
    survey_template_data["organization_id"] = current_user.organization_id
    survey_template_data["created_by"] = current_user.id
    
    survey_template = SurveyTemplate.model_validate(survey_template_data)
    session.add(survey_template)
    session.commit()
    session.refresh(survey_template)
    return survey_template


@router.get("/active", response_model=SurveyTemplatesPublic)
def read_active_survey_templates(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve only active survey templates for the current user's organization.
    Admins and providers can view active templates.
    """
    # Only allow admins and providers to view templates
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view survey templates"
        )
    count_statement = select(func.count()).select_from(SurveyTemplate).where(
        SurveyTemplate.organization_id == current_user.organization_id,
        SurveyTemplate.active == True
    )
    count = session.exec(count_statement).one()

    statement = (
        select(SurveyTemplate)
        .where(
            SurveyTemplate.organization_id == current_user.organization_id,
            SurveyTemplate.active == True
        )
        .offset(skip)
        .limit(limit)
    )
    survey_templates = session.exec(statement).all()

    return SurveyTemplatesPublic(data=survey_templates, count=count)


@router.get("/{survey_template_id}", response_model=SurveyTemplatePublic)
def read_survey_template(
    survey_template_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get survey template by ID. Admins and providers can view templates.
    """
    # Only allow admins and providers to view templates
    if not current_user.is_superuser and current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=403, detail="Only admins and providers can view survey templates"
        )
    survey_template = session.get(SurveyTemplate, survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return survey_template


@router.patch(
    "/{survey_template_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SurveyTemplatePublic,
)
def update_survey_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    survey_template_id: uuid.UUID,
    survey_template_in: SurveyTemplateUpdate,
) -> Any:
    """
    Update a survey template. Admin access only for MVP.
    """
    survey_template = session.get(SurveyTemplate, survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = survey_template_in.model_dump(exclude_unset=True)
    survey_template.sqlmodel_update(update_dict)
    session.add(survey_template)
    session.commit()
    session.refresh(survey_template)
    return survey_template


@router.delete(
    "/{survey_template_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_survey_template(
    session: SessionDep, current_user: CurrentUser, survey_template_id: uuid.UUID
) -> Message:
    """
    Delete a survey template. Admin access only for MVP.
    """
    survey_template = session.get(SurveyTemplate, survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(survey_template)
    session.commit()
    return Message(message="Survey template deleted successfully")


@router.post(
    "/{survey_template_id}/duplicate",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SurveyTemplatePublic,
)
def duplicate_survey_template(
    survey_template_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Create a duplicate of an existing survey template. Admin access only for MVP.
    """
    
    original_template = session.get(SurveyTemplate, survey_template_id)
    if not original_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if original_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create a new template with copied data
    template_data = {
        "name": f"{original_template.name} (Copy)",
        "description": original_template.description,
        "questions": original_template.questions,
        "triggers": original_template.triggers,
        "delivery_settings": original_template.delivery_settings,
        "organization_id": current_user.organization_id,
        "created_by": current_user.id,
        "active": False,  # Start as inactive
        "version": 1,  # Reset version
    }
    
    new_template = SurveyTemplate.model_validate(template_data)
    session.add(new_template)
    session.commit()
    session.refresh(new_template)
    return new_template


@router.patch(
    "/{survey_template_id}/activate",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SurveyTemplatePublic,
)
def activate_survey_template(
    survey_template_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Activate a survey template. Admin access only for MVP.
    """
    
    survey_template = session.get(SurveyTemplate, survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    survey_template.active = True
    session.add(survey_template)
    session.commit()
    session.refresh(survey_template)
    return survey_template


@router.patch(
    "/{survey_template_id}/deactivate",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SurveyTemplatePublic,
)
def deactivate_survey_template(
    survey_template_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Deactivate a survey template. Admin access only for MVP.
    """
    
    survey_template = session.get(SurveyTemplate, survey_template_id)
    if not survey_template:
        raise HTTPException(status_code=404, detail="Survey template not found")
    
    if survey_template.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    survey_template.active = False
    session.add(survey_template)
    session.commit()
    session.refresh(survey_template)
    return survey_template
