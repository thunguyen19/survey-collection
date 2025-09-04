import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import OrganizationCreate, SurveyTemplateCreate, UserCreate
from app.tests.utils.user import create_user_create
from app.tests.utils.utils import random_lower_string


def test_create_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization first
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    data = {
        "name": f"Test Template {random_lower_string()}",
        "description": "Test survey template",
        "organization_id": str(organization.id),
        "questions": {
            "q1": {"type": "text", "question": "How was your experience?"},
            "q2": {"type": "rating", "question": "Rate from 1-5", "scale": 5}
        },
        "active": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/survey-templates/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["active"] == data["active"]
    assert "id" in content
    assert "created_at" in content


def test_create_survey_template_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {
        "name": f"Test Template {random_lower_string()}",
        "organization_id": str(uuid.uuid4()),
    }
    response = client.post(
        f"{settings.API_V1_STR}/survey-templates/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_read_survey_templates_admin(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and template
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    template_data = SurveyTemplateCreate(
        name=f"Test Template {random_lower_string()}",
        organization_id=organization.id,
        created_by=uuid.uuid4(),  # Will be overridden by backend
        questions={"q1": {"type": "text", "question": "Test question"}},
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    response = client.get(
        f"{settings.API_V1_STR}/survey-templates/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 1
    assert content["count"] >= 1


def test_read_survey_templates_non_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/survey-templates/",
        headers=normal_user_token_headers,
    )
    # Should fail if user is not admin or provider
    assert response.status_code in [403, 400]


def test_read_active_survey_templates(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/survey-templates/active",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # All returned templates should be active
    for template in content["data"]:
        assert template["active"] is True


def test_read_survey_template_by_id(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and template
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
        f"{settings.API_V1_STR}/survey-templates/{template.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == template.name
    assert content["id"] == str(template.id)


def test_read_survey_template_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/survey-templates/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_update_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and template
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
    
    update_data = {
        "name": f"Updated Template {random_lower_string()}",
        "description": "Updated description",
        "active": False,
    }
    response = client.patch(
        f"{settings.API_V1_STR}/survey-templates/{template.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]
    assert content["active"] == update_data["active"]


def test_delete_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and template
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
    
    response = client.delete(
        f"{settings.API_V1_STR}/survey-templates/{template.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify template is deleted
    response = client.get(
        f"{settings.API_V1_STR}/survey-templates/{template.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_duplicate_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and template
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
    
    response = client.post(
        f"{settings.API_V1_STR}/survey-templates/{template.id}/duplicate",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == f"{template.name} (Copy)"
    assert content["active"] is False  # Duplicates should start as inactive
    assert content["version"] == 1  # Reset version
    assert content["id"] != str(template.id)  # Should be a new template


def test_activate_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and inactive template
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
        active=False,
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    response = client.patch(
        f"{settings.API_V1_STR}/survey-templates/{template.id}/activate",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["active"] is True


def test_deactivate_survey_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create organization and active template
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
        active=True,
    )
    template = crud.create_survey_template(session=db, survey_template_create=template_data)
    
    response = client.patch(
        f"{settings.API_V1_STR}/survey-templates/{template.id}/deactivate",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["active"] is False

