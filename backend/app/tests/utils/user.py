import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def create_user_create(
    email: str | None = None,
    password: str | None = None,
    full_name: str | None = None,
    is_superuser: bool = False,
    organization_id: uuid.UUID | None = None
) -> UserCreate:
    """Helper function to create UserCreate objects with all required fields."""
    return UserCreate(
        email=email or random_email(),
        password=password or random_lower_string(),
        full_name=full_name or f"Test User {random_lower_string()}",
        organization_id=organization_id or uuid.UUID("00000000-0000-0000-0000-000000000000"),
        is_superuser=is_superuser
    )


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    user_in = create_user_create()
    user = crud.create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.get_user_by_email(session=db, email=email)
    if not user:
        user_in_create = create_user_create(
            email=email,
            password=password,
            full_name=f"Test User {email.split('@')[0]}"
        )
        user = crud.create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        user = crud.update_user(session=db, db_user=user, user_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
