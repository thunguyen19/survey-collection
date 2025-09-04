import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    OrganizationCreate, 
    SurveyTemplateCreate, 
    FeedbackSessionCreate,
    UserCreate
)
from app.tests.utils.user import create_user_create
from app.tests.utils.utils import random_lower_string


def test_create_feedback_session(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and survey template
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    # Create feedback session
    session_data = {
        "survey_template_id": str(template.id),
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "delivery_method": "email",
        "metadata": {"test": "data"},
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/feedback-sessions/",
        headers=superuser_token_headers,
        json=session_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["patient_name"] == session_data["patient_name"]
    assert content["patient_email"] == session_data["patient_email"]
    assert content["delivery_method"] == session_data["delivery_method"]
    assert "completion_token" in content
    assert "id" in content


def test_create_feedback_session_non_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    session_data = {
        "survey_template_id": str(uuid.uuid4()),
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/feedback-sessions/",
        headers=normal_user_token_headers,
        json=session_data,
    )
    assert response.status_code == 403


def test_read_feedback_sessions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)


def test_read_feedback_sessions_non_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/",
        headers=normal_user_token_headers,
    )
    # Should fail if user is not admin or provider
    assert response.status_code in [403, 400]


def test_read_feedback_session_by_id(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/{feedback_session.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["patient_name"] == feedback_session.patient_name
    assert content["id"] == str(feedback_session.id)


def test_read_feedback_session_by_token(
    client: TestClient, db: Session
) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    # Test public access by token (no authentication required)
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/by-token/{feedback_session.completion_token}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["patient_name"] == feedback_session.patient_name
    assert content["id"] == str(feedback_session.id)


def test_read_feedback_session_by_invalid_token(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/by-token/{uuid.uuid4()}",
    )
    assert response.status_code == 404


def test_update_feedback_session(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    update_data = {
        "patient_name": "Jane Doe",
        "notes": "Updated notes",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/feedback-sessions/{feedback_session.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["patient_name"] == update_data["patient_name"]
    assert content["notes"] == update_data["notes"]


def test_complete_feedback_session(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    response = client.patch(
        f"{settings.API_V1_STR}/feedback-sessions/{feedback_session.id}/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "completed"
    assert content["completed_at"] is not None


def test_complete_feedback_session_by_token(client: TestClient, db: Session) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    # Test public completion by token (no authentication required)
    response = client.patch(
        f"{settings.API_V1_STR}/feedback-sessions/by-token/{feedback_session.completion_token}/complete",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "completed"


def test_delete_feedback_session(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, and session
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    response = client.delete(
        f"{settings.API_V1_STR}/feedback-sessions/{feedback_session.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify session is deleted
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/{feedback_session.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_get_organization_feedback_stats(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-sessions/stats/organization",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "total_sessions" in content
    assert "completed_sessions" in content
    assert "completion_rate" in content
    assert "avg_completion_time_hours" in content

