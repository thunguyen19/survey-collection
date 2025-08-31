import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, JSON, Column
from sqlalchemy import ARRAY, String, Text, LargeBinary


# Enums
class UserType(str, Enum):
    PROVIDER = "provider"
    PATIENT = "patient"
    ADMIN = "admin"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class FeedbackSessionStatus(str, Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    IN_PERSON = "in_person"


# Organization Models
class OrganizationBase(SQLModel):
    name: str = Field(max_length=255)
    type: Optional[str] = Field(default=None, max_length=100)
    subscription_tier: Optional[str] = Field(default="basic", max_length=50)
    active: bool = Field(default=True)


class OrganizationCreate(OrganizationBase):
    settings: Optional[dict] = Field(default_factory=dict)


class OrganizationUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    type: Optional[str] = Field(default=None, max_length=100)
    settings: Optional[dict] = None
    subscription_tier: Optional[str] = Field(default=None, max_length=50)
    active: Optional[bool] = None


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    settings: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="organization", cascade_delete=True)
    survey_templates: List["SurveyTemplate"] = Relationship(back_populates="organization", cascade_delete=True)


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    settings: Optional[dict]
    created_at: datetime
    updated_at: datetime


class OrganizationsPublic(SQLModel):
    data: List[OrganizationPublic]
    count: int


# User Models
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    user_type: UserType
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    external_id: Optional[str] = Field(default=None, max_length=255)
    
    # Provider-specific fields
    title: Optional[str] = Field(default=None, max_length=100)
    specialty: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    npi_number: Optional[str] = Field(default=None, max_length=20)
    
    # Patient-specific fields
    preferred_contact_method: Optional[str] = Field(default=None, max_length=50)
    language_preference: Optional[str] = Field(default="en", max_length=10)
    opt_out_status: bool = Field(default=False)
    opt_out_date: Optional[datetime] = None
    
    # Auth/Admin fields
    role: Optional[str] = Field(default=None, max_length=50)
    active: bool = Field(default=True)


class UserCreate(UserBase):
    organization_id: uuid.UUID
    password: str = Field(min_length=8, max_length=40)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    permissions: Optional[dict] = Field(default_factory=dict)


class UserRegister(SQLModel):
    organization_id: uuid.UUID
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    user_type: UserType
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=100)
    specialty: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    preferred_contact_method: Optional[str] = Field(default=None, max_length=50)
    language_preference: Optional[str] = Field(default=None, max_length=10)
    opt_out_status: Optional[bool] = None
    role: Optional[str] = Field(default=None, max_length=50)
    active: Optional[bool] = None
    permissions: Optional[dict] = None


class UserUpdateMe(SQLModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    preferred_contact_method: Optional[str] = Field(default=None, max_length=50)
    language_preference: Optional[str] = Field(default=None, max_length=10)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", nullable=False)
    hashed_password: str
    phone_number_encrypted: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    last_login: Optional[datetime] = None
    permissions: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Organization = Relationship(back_populates="users")
    patient_appointments: List["Appointment"] = Relationship(
        back_populates="patient",
        sa_relationship_kwargs={"foreign_keys": "[Appointment.patient_id]"}
    )
    provider_appointments: List["Appointment"] = Relationship(
        back_populates="provider",
        sa_relationship_kwargs={"foreign_keys": "[Appointment.provider_id]"}
    )
    created_survey_templates: List["SurveyTemplate"] = Relationship(back_populates="creator")


class UserPublic(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int


# Appointment Models
class AppointmentBase(SQLModel):
    external_appointment_id: Optional[str] = Field(default=None, max_length=255)
    appointment_date: datetime
    appointment_type: Optional[str] = Field(default=None, max_length=100)
    chief_complaint: Optional[str] = None
    visit_duration_minutes: Optional[int] = None
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)


class AppointmentCreate(AppointmentBase):
    patient_id: uuid.UUID
    provider_id: uuid.UUID
    diagnosis_codes: Optional[List[str]] = Field(default_factory=list)
    diagnosis_descriptions: Optional[List[str]] = Field(default_factory=list)


class AppointmentUpdate(SQLModel):
    appointment_date: Optional[datetime] = None
    appointment_type: Optional[str] = Field(default=None, max_length=100)
    diagnosis_codes: Optional[List[str]] = None
    diagnosis_descriptions: Optional[List[str]] = None
    chief_complaint: Optional[str] = None
    visit_duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None


class Appointment(AppointmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    provider_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    diagnosis_codes: Optional[List[str]] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    diagnosis_descriptions: Optional[List[str]] = Field(default_factory=list, sa_column=Column(ARRAY(Text)))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    patient: User = Relationship(
        back_populates="patient_appointments",
        sa_relationship_kwargs={"foreign_keys": "[Appointment.patient_id]"}
    )
    provider: User = Relationship(
        back_populates="provider_appointments",
        sa_relationship_kwargs={"foreign_keys": "[Appointment.provider_id]"}
    )
    feedback_session: Optional["FeedbackSession"] = Relationship(back_populates="appointment")


class AppointmentPublic(AppointmentBase):
    id: uuid.UUID
    patient_id: uuid.UUID
    provider_id: uuid.UUID
    diagnosis_codes: Optional[List[str]]
    diagnosis_descriptions: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class AppointmentsPublic(SQLModel):
    data: List[AppointmentPublic]
    count: int


# Survey Template Models
class SurveyTemplateBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    active: bool = Field(default=True)
    version: int = Field(default=1)


class SurveyTemplateCreate(SurveyTemplateBase):
    organization_id: uuid.UUID
    questions: dict = Field(default_factory=dict)
    triggers: dict = Field(default_factory=dict)
    delivery_settings: dict = Field(default_factory=dict)
    created_by: uuid.UUID


class SurveyTemplateUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    questions: Optional[dict] = None
    triggers: Optional[dict] = None
    delivery_settings: Optional[dict] = None
    active: Optional[bool] = None
    version: Optional[int] = None


class SurveyTemplate(SurveyTemplateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", nullable=False)
    questions: dict = Field(default_factory=dict, sa_column=Column(JSON))
    triggers: dict = Field(default_factory=dict, sa_column=Column(JSON))
    delivery_settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Organization = Relationship(back_populates="survey_templates")
    creator: User = Relationship(back_populates="created_survey_templates")
    feedback_sessions: List["FeedbackSession"] = Relationship(back_populates="survey_template")


class SurveyTemplatePublic(SurveyTemplateBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    questions: dict
    triggers: dict
    delivery_settings: dict
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SurveyTemplatesPublic(SQLModel):
    data: List[SurveyTemplatePublic]
    count: int


# Feedback Response Type Models
class FeedbackResponseTypeBase(SQLModel):
    type_name: str = Field(unique=True, max_length=100)
    type_category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    active: bool = Field(default=True)


class FeedbackResponseTypeCreate(FeedbackResponseTypeBase):
    validation_rules: dict = Field(default_factory=dict)
    display_options: dict = Field(default_factory=dict)


class FeedbackResponseTypeUpdate(SQLModel):
    type_name: Optional[str] = Field(default=None, max_length=100)
    type_category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    validation_rules: Optional[dict] = None
    display_options: Optional[dict] = None
    active: Optional[bool] = None


class FeedbackResponseType(FeedbackResponseTypeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    validation_rules: dict = Field(default_factory=dict, sa_column=Column(JSON))
    display_options: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    feedback_responses: List["FeedbackResponse"] = Relationship(back_populates="response_type")


class FeedbackResponseTypePublic(FeedbackResponseTypeBase):
    id: uuid.UUID
    validation_rules: dict
    display_options: dict
    created_at: datetime
    updated_at: datetime


class FeedbackResponseTypesPublic(SQLModel):
    data: List[FeedbackResponseTypePublic]
    count: int


# Feedback Session Models
class FeedbackSessionBase(SQLModel):
    status: FeedbackSessionStatus = Field(default=FeedbackSessionStatus.INITIATED)
    delivery_method: Optional[DeliveryMethod] = None
    delivery_attempts: int = Field(default=0)


class FeedbackSessionCreate(FeedbackSessionBase):
    appointment_id: uuid.UUID
    survey_template_id: uuid.UUID
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    expired_at: Optional[datetime] = None


class FeedbackSessionUpdate(SQLModel):
    status: Optional[FeedbackSessionStatus] = None
    first_response_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    delivery_method: Optional[DeliveryMethod] = None
    delivery_attempts: Optional[int] = None
    last_delivery_attempt: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    completion_time_seconds: Optional[int] = None


class FeedbackSession(FeedbackSessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    appointment_id: uuid.UUID = Field(foreign_key="appointment.id", nullable=False)
    survey_template_id: uuid.UUID = Field(foreign_key="surveytemplate.id", nullable=False)
    completion_token: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True)
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    first_response_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    last_delivery_attempt: Optional[datetime] = None
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 compatible
    user_agent: Optional[str] = None
    completion_time_seconds: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    appointment: Appointment = Relationship(back_populates="feedback_session")
    survey_template: SurveyTemplate = Relationship(back_populates="feedback_sessions")
    feedback_responses: List["FeedbackResponse"] = Relationship(back_populates="session", cascade_delete=True)


class FeedbackSessionPublic(FeedbackSessionBase):
    id: uuid.UUID
    appointment_id: uuid.UUID
    survey_template_id: uuid.UUID
    completion_token: uuid.UUID
    initiated_at: datetime
    first_response_at: Optional[datetime]
    completed_at: Optional[datetime]
    expired_at: Optional[datetime]
    last_delivery_attempt: Optional[datetime]
    completion_time_seconds: Optional[int]
    created_at: datetime


class FeedbackSessionsPublic(SQLModel):
    data: List[FeedbackSessionPublic]
    count: int


# Feedback Response Models
class FeedbackResponseBase(SQLModel):
    question_id: str = Field(max_length=255)
    response_text: Optional[str] = None
    response_time_seconds: Optional[int] = None


class FeedbackResponseCreate(FeedbackResponseBase):
    session_id: uuid.UUID
    response_type_id: uuid.UUID
    response_value: dict = Field(default_factory=dict)


class FeedbackResponseUpdate(SQLModel):
    response_value: Optional[dict] = None
    response_text: Optional[str] = None
    ai_analysis: Optional[dict] = None
    response_time_seconds: Optional[int] = None


class FeedbackResponse(FeedbackResponseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="feedbacksession.id", nullable=False)
    response_type_id: uuid.UUID = Field(foreign_key="feedbackresponsetype.id", nullable=False)
    response_value: dict = Field(default_factory=dict, sa_column=Column(JSON))
    ai_analysis: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    session: FeedbackSession = Relationship(back_populates="feedback_responses")
    response_type: FeedbackResponseType = Relationship(back_populates="feedback_responses")


class FeedbackResponsePublic(FeedbackResponseBase):
    id: uuid.UUID
    session_id: uuid.UUID
    response_type_id: uuid.UUID
    response_value: dict
    ai_analysis: Optional[dict]
    created_at: datetime


class FeedbackResponsesPublic(SQLModel):
    data: List[FeedbackResponsePublic]
    count: int


# Auth Models (kept from original)
class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)