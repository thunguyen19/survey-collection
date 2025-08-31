import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Organization,
    OrganizationCreate,
    OrganizationPublic,
    OrganizationsPublic,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=OrganizationsPublic,
)
def read_organizations(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve organizations. Only superusers can access this.
    """
    count_statement = select(func.count()).select_from(Organization)
    count = session.exec(count_statement).one()

    statement = select(Organization).offset(skip).limit(limit)
    organizations = session.exec(statement).all()

    return OrganizationsPublic(data=organizations, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=OrganizationPublic,
)
def create_organization(
    *, session: SessionDep, organization_in: OrganizationCreate
) -> Any:
    """
    Create new organization. Only superusers can create organizations.
    """
    organization = Organization.model_validate(organization_in)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    return organization


@router.get("/me", response_model=OrganizationPublic)
def read_my_organization(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user's organization.
    """
    organization = session.get(Organization, current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/{organization_id}", response_model=OrganizationPublic)
def read_organization(
    organization_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get organization by ID. Users can only access their own organization unless they're superusers.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Allow access if user belongs to this organization or is superuser
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return organization


@router.patch(
    "/{organization_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=OrganizationPublic,
)
def update_organization(
    *,
    session: SessionDep,
    organization_id: uuid.UUID,
    organization_in: OrganizationUpdate,
) -> Any:
    """
    Update an organization. Only superusers can update organizations.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_dict = organization_in.model_dump(exclude_unset=True)
    organization.sqlmodel_update(update_dict)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    return organization


@router.delete(
    "/{organization_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_organization(
    session: SessionDep, organization_id: uuid.UUID
) -> Message:
    """
    Delete an organization. Only superusers can delete organizations.
    This will cascade delete all related data (users, surveys, etc.).
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    session.delete(organization)
    session.commit()
    return Message(message="Organization deleted successfully")
