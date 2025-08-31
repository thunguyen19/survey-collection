import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    # Existing models
    Item, ItemCreate, User, UserCreate, UserUpdate,
    # New models for MVP (admin-only access)
    Organization, OrganizationCreate, OrganizationUpdate,
    SurveyTemplate, SurveyTemplateCreate, SurveyTemplateUpdate,
    FeedbackSession, FeedbackSessionCreate, FeedbackSessionUpdate,
    FeedbackResponse, FeedbackResponseCreate, FeedbackResponseUpdate,
    FeedbackResponseType, FeedbackResponseTypeCreate, FeedbackResponseTypeUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Organization CRUD operations
def create_organization(*, session: Session, organization_create: OrganizationCreate) -> Organization:
    db_obj = Organization.model_validate(organization_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_organization_by_id(*, session: Session, organization_id: uuid.UUID) -> Organization | None:
    return session.get(Organization, organization_id)


def update_organization(*, session: Session, db_organization: Organization, organization_in: OrganizationUpdate) -> Organization:
    organization_data = organization_in.model_dump(exclude_unset=True)
    db_organization.sqlmodel_update(organization_data)
    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


# Appointment CRUD operations (removed for MVP - admin-only access)


# Survey Template CRUD operations
def create_survey_template(*, session: Session, survey_template_create: SurveyTemplateCreate) -> SurveyTemplate:
    db_obj = SurveyTemplate.model_validate(survey_template_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_survey_template_by_id(*, session: Session, template_id: uuid.UUID) -> SurveyTemplate | None:
    return session.get(SurveyTemplate, template_id)


def update_survey_template(*, session: Session, db_template: SurveyTemplate, template_in: SurveyTemplateUpdate) -> SurveyTemplate:
    template_data = template_in.model_dump(exclude_unset=True)
    db_template.sqlmodel_update(template_data)
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


def get_survey_templates_by_organization(*, session: Session, organization_id: uuid.UUID, active_only: bool = True) -> list[SurveyTemplate]:
    statement = select(SurveyTemplate).where(SurveyTemplate.organization_id == organization_id)
    if active_only:
        statement = statement.where(SurveyTemplate.active == True)
    return list(session.exec(statement).all())


# Feedback Session CRUD operations
def create_feedback_session(*, session: Session, feedback_session_create: FeedbackSessionCreate) -> FeedbackSession:
    db_obj = FeedbackSession.model_validate(feedback_session_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_feedback_session_by_id(*, session: Session, session_id: uuid.UUID) -> FeedbackSession | None:
    return session.get(FeedbackSession, session_id)


def get_feedback_session_by_token(*, session: Session, completion_token: uuid.UUID) -> FeedbackSession | None:
    statement = select(FeedbackSession).where(FeedbackSession.completion_token == completion_token)
    return session.exec(statement).first()


def get_feedback_session_by_appointment(*, session: Session, appointment_id: uuid.UUID) -> FeedbackSession | None:
    statement = select(FeedbackSession).where(FeedbackSession.appointment_id == appointment_id)
    return session.exec(statement).first()


def update_feedback_session(*, session: Session, db_session: FeedbackSession, session_in: FeedbackSessionUpdate) -> FeedbackSession:
    session_data = session_in.model_dump(exclude_unset=True)
    db_session.sqlmodel_update(session_data)
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


# Feedback Response CRUD operations
def create_feedback_response(*, session: Session, feedback_response_create: FeedbackResponseCreate) -> FeedbackResponse:
    db_obj = FeedbackResponse.model_validate(feedback_response_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_feedback_response_by_id(*, session: Session, response_id: uuid.UUID) -> FeedbackResponse | None:
    return session.get(FeedbackResponse, response_id)


def get_feedback_responses_by_session(*, session: Session, session_id: uuid.UUID) -> list[FeedbackResponse]:
    statement = select(FeedbackResponse).where(FeedbackResponse.session_id == session_id)
    return list(session.exec(statement).all())


def update_feedback_response(*, session: Session, db_response: FeedbackResponse, response_in: FeedbackResponseUpdate) -> FeedbackResponse:
    response_data = response_in.model_dump(exclude_unset=True)
    db_response.sqlmodel_update(response_data)
    session.add(db_response)
    session.commit()
    session.refresh(db_response)
    return db_response


# Feedback Response Type CRUD operations
def create_feedback_response_type(*, session: Session, response_type_create: FeedbackResponseTypeCreate) -> FeedbackResponseType:
    db_obj = FeedbackResponseType.model_validate(response_type_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_feedback_response_type_by_id(*, session: Session, type_id: uuid.UUID) -> FeedbackResponseType | None:
    return session.get(FeedbackResponseType, type_id)


def get_feedback_response_type_by_name(*, session: Session, type_name: str) -> FeedbackResponseType | None:
    statement = select(FeedbackResponseType).where(FeedbackResponseType.type_name == type_name)
    return session.exec(statement).first()


def get_feedback_response_types_by_category(*, session: Session, category: str, active_only: bool = True) -> list[FeedbackResponseType]:
    statement = select(FeedbackResponseType).where(FeedbackResponseType.type_category == category)
    if active_only:
        statement = statement.where(FeedbackResponseType.active == True)
    return list(session.exec(statement).all())


def update_feedback_response_type(*, session: Session, db_type: FeedbackResponseType, type_in: FeedbackResponseTypeUpdate) -> FeedbackResponseType:
    type_data = type_in.model_dump(exclude_unset=True)
    db_type.sqlmodel_update(type_data)
    session.add(db_type)
    session.commit()
    session.refresh(db_type)
    return db_type


def get_all_feedback_response_types(*, session: Session, active_only: bool = True) -> list[FeedbackResponseType]:
    statement = select(FeedbackResponseType)
    if active_only:
        statement = statement.where(FeedbackResponseType.active == True)
    return list(session.exec(statement).all())
