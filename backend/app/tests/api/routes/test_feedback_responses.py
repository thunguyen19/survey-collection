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
    FeedbackResponseCreate
)
from app.tests.utils.utils import random_lower_string


def test_create_feedback_response(
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
    
    # Create feedback response (public endpoint - no auth required)
    response_data = {
        "feedback_session_id": str(feedback_session.id),
        "question_id": "q1",
        "response_value": "Great experience!",
        "response_type": "text",
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/feedback-responses/",
        json=response_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["question_id"] == response_data["question_id"]
    assert content["response_value"] == response_data["response_value"]
    assert content["response_type"] == response_data["response_type"]
    assert "id" in content


def test_create_feedback_responses_batch(
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
        questions={
            "q1": {"type": "text", "question": "Test question 1"},
            "q2": {"type": "rating", "question": "Test question 2"}
        },
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    session_data = FeedbackSessionCreate(
        survey_template_id=template.id,
        patient_name="John Doe",
        patient_email="john@example.com",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    feedback_session = crud.create_feedback_session(session=db, feedback_session_in=session_data)
    
    # Create batch feedback responses (public endpoint - no auth required)
    responses_data = {
        "feedback_session_id": str(feedback_session.id),
        "responses": [
            {
                "question_id": "q1",
                "response_value": "Great experience!",
                "response_type": "text",
            },
            {
                "question_id": "q2",
                "response_value": "5",
                "response_type": "rating",
            }
        ]
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/feedback-responses/batch",
        json=responses_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2
    assert content[0]["question_id"] == "q1"
    assert content[1]["question_id"] == "q2"


def test_read_feedback_responses(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)


def test_read_feedback_responses_non_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/",
        headers=normal_user_token_headers,
    )
    # Should fail if user is not admin or provider
    assert response.status_code in [403, 400]


def test_read_feedback_responses_by_session(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, session, and response
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
    
    response_data = FeedbackResponseCreate(
        feedback_session_id=feedback_session.id,
        question_id="q1",
        response_value="Great experience!",
        response_type="text",
    )
    feedback_response = crud.create_feedback_response(session=db, response_in=response_data)
    
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/session/{feedback_session.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert len(content["data"]) >= 1
    
    # Check if our response is in the results
    response_ids = [r["id"] for r in content["data"]]
    assert str(feedback_response.id) in response_ids


def test_read_feedback_response_by_id(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, session, and response
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
    
    response_data = FeedbackResponseCreate(
        feedback_session_id=feedback_session.id,
        question_id="q1",
        response_value="Great experience!",
        response_type="text",
    )
    feedback_response = crud.create_feedback_response(session=db, response_in=response_data)
    
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/{feedback_response.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["question_id"] == feedback_response.question_id
    assert content["response_value"] == feedback_response.response_value
    assert content["id"] == str(feedback_response.id)


def test_read_feedback_response_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_update_feedback_response(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, session, and response
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
    
    response_data = FeedbackResponseCreate(
        feedback_session_id=feedback_session.id,
        question_id="q1",
        response_value="Great experience!",
        response_type="text",
    )
    feedback_response = crud.create_feedback_response(session=db, response_in=response_data)
    
    update_data = {
        "response_value": "Updated response!",
        "notes": "Admin updated this response",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/feedback-responses/{feedback_response.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["response_value"] == update_data["response_value"]
    assert content["notes"] == update_data["notes"]


def test_delete_feedback_response(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization, template, session, and response
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
    
    response_data = FeedbackResponseCreate(
        feedback_session_id=feedback_session.id,
        question_id="q1",
        response_value="Great experience!",
        response_type="text",
    )
    feedback_response = crud.create_feedback_response(session=db, response_in=response_data)
    
    response = client.delete(
        f"{settings.API_V1_STR}/feedback-responses/{feedback_response.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify response is deleted
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/{feedback_response.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_get_question_analytics(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create some test data first
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
    
    response = client.get(
        f"{settings.API_V1_STR}/feedback-responses/analytics/question/q1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "question_id" in content
    assert "total_responses" in content
    assert "response_distribution" in content

