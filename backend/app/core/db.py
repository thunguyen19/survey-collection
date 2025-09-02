import uuid
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Organization

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Create default organization if it doesn't exist
    default_org_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    organization = session.exec(
        select(Organization).where(Organization.id == default_org_id)
    ).first()
    if not organization:
        organization = Organization(
            id=default_org_id,
            name="Default Organization",
            organization_type="healthcare",
            active=True
        )
        session.add(organization)
        session.commit()
        session.refresh(organization)

    # Create first superuser if it doesn't exist
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="System Administrator",
            organization_id=default_org_id,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
