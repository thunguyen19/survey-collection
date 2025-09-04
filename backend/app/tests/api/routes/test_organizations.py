import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import Organization, OrganizationCreate, OrganizationUpdate
from app.tests.utils.utils import random_lower_string


def test_create_organization(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "name": f"Test Org {random_lower_string()}",
        "organization_type": "healthcare",
        "description": "Test organization for API testing",
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["organization_type"] == data["organization_type"]
    assert content["description"] == data["description"]
    assert "id" in content


def test_create_organization_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {
        "name": f"Test Org {random_lower_string()}",
        "organization_type": "healthcare",
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_read_organizations(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    response = client.get(
        f"{settings.API_V1_STR}/organizations/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 1
    assert content["count"] >= 1
    
    # Check if our created organization is in the response
    org_names = [org["name"] for org in content["data"]]
    assert organization.name in org_names


def test_read_organizations_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/organizations/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403


def test_read_organization_by_id(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    response = client.get(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == organization.name
    assert content["id"] == str(organization.id)


def test_read_organization_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/organizations/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_read_my_organization(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/organizations/me",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "id" in content
    assert "name" in content


def test_update_organization(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    data = {
        "name": f"Updated Org {random_lower_string()}",
        "description": "Updated description",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]


def test_update_organization_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    data = {"name": "Should not be allowed"}
    response = client.patch(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_delete_organization(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    response = client.delete(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify organization is deleted
    response = client.get(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_delete_organization_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    # Create test organization
    org_create = OrganizationCreate(
        name=f"Test Org {random_lower_string()}",
        organization_type="healthcare",
    )
    organization = crud.create_organization(session=db, organization_in=org_create)
    
    response = client.delete(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403

