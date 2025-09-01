## Data Model

```mermaid
erDiagram
    ORGANIZATIONS {
        UUID id PK
        VARCHAR name
        VARCHAR type
        JSONB settings
        VARCHAR subscription_tier
        TIMESTAMP created_at
        TIMESTAMP updated_at
        BOOLEAN active
    }

    USERS {
        UUID id PK
        UUID organization_id FK
        VARCHAR user_type
        VARCHAR first_name
        VARCHAR last_name
        VARCHAR middle_name
        VARCHAR email
        BYTEA phone_number_encrypted
        VARCHAR external_id
        VARCHAR title
        VARCHAR specialty
        VARCHAR department
        VARCHAR npi_number
        VARCHAR preferred_contact_method
        VARCHAR language_preference
        BOOLEAN opt_out_status
        TIMESTAMP opt_out_date
        VARCHAR role
        VARCHAR password_hash
        TIMESTAMP last_login
        JSONB permissions
        BOOLEAN active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    APPOINTMENTS {
        UUID id PK
        UUID patient_id FK
        UUID provider_id FK
        VARCHAR external_appointment_id
        TIMESTAMP appointment_date
        VARCHAR appointment_type
        VARCHAR[] diagnosis_codes
        TEXT[] diagnosis_descriptions
        TEXT chief_complaint
        INTEGER visit_duration_minutes
        VARCHAR status
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    SURVEY_TEMPLATES {
        UUID id PK
        UUID organization_id FK
        VARCHAR name
        TEXT description
        JSONB questions
        JSONB triggers
        JSONB delivery_settings
        BOOLEAN active
        INTEGER version
        UUID created_by FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    FEEDBACK_SESSIONS {
        UUID id PK
        UUID appointment_id FK
        UUID survey_template_id FK
        UUID completion_token UK
        TIMESTAMP initiated_at
        TIMESTAMP first_response_at
        TIMESTAMP completed_at
        TIMESTAMP expired_at
        VARCHAR status
        VARCHAR delivery_method
        INTEGER delivery_attempts
        TIMESTAMP last_delivery_attempt
        INET ip_address
        TEXT user_agent
        INTEGER completion_time_seconds
        TIMESTAMP created_at
    }

    FEEDBACK_RESPONSE_TYPES {
        UUID id PK
        VARCHAR type_name UK
        VARCHAR type_category
        TEXT description
        JSONB validation_rules
        JSONB display_options
        BOOLEAN active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    FEEDBACK_RESPONSES {
        UUID id PK
        UUID session_id FK
        UUID response_type_id FK
        VARCHAR question_id
        JSONB response_value
        TEXT response_text
        JSONB ai_analysis
        INTEGER response_time_seconds
        TIMESTAMP created_at
    }

    %% Core Relationships
    ORGANIZATIONS ||--o{ USERS : "has"

    USERS ||--o{ APPOINTMENTS : "patient_appointments"
    USERS ||--o{ APPOINTMENTS : "provider_appointments"

    APPOINTMENTS ||--o{ FEEDBACK_SESSIONS : "triggers"
    SURVEY_TEMPLATES ||--o{ FEEDBACK_SESSIONS : "defines"

    FEEDBACK_SESSIONS ||--o{ FEEDBACK_RESPONSES : "contains"
    FEEDBACK_RESPONSE_TYPES ||--o{ FEEDBACK_RESPONSES : "defines_type"

    USERS ||--o{ SURVEY_TEMPLATES : "creates"

    %% Cardinality Annotations
    ORGANIZATIONS {
        string org_constraint "1 to many with users"
    }
    
    APPOINTMENTS {
        string appointment_constraint "1 appointment can have 1 feedback session"
    }
    
    FEEDBACK_SESSIONS {
        string session_constraint "1 session can have many responses"
    }

    FEEDBACK_RESPONSE_TYPES {
        string type_constraint "Examples: yes_no, rating_scale, text_input, multiple_choice"
    }

    USERS {
        string type_constraint "user_type field: 'provider', 'patient', 'admin'"
    }
```

I'll read the updated data model file to provide you with a current summary.

[1 tool called]

Based on the updated data model, here's a summary of your survey collection application's entities:

## Data Model Summary

### Core Entities

**1. Organizations**
- Multi-tenant container for all application data
- Fields: `name`, `type`, `settings` (JSONB), `subscription_tier`, `active` status, timestamps
- Acts as the root entity for data isolation

**2. Users** *(Consolidated entity combining providers, patients, and admin users)*
- Single unified user table with `user_type` field ('provider', 'patient', 'admin')
- Universal fields: `first_name`, `last_name`, `middle_name`, `email`, `phone_number_encrypted`, `external_id`
- Provider-specific: `title`, `specialty`, `department`, `npi_number`
- Patient-specific: `preferred_contact_method`, `language_preference`, `opt_out_status`, `opt_out_date`
- Auth/Admin: `role`, `password_hash`, `last_login`, `permissions` (JSONB)
- Status: `active`, timestamps

**3. Appointments**
- Care encounters between patients and providers (both referenced as `USERS`)
- Fields: `patient_id`, `provider_id`, `external_appointment_id`, `appointment_date`, `appointment_type`
- Clinical data: `diagnosis_codes` (array), `diagnosis_descriptions` (array), `chief_complaint`, `visit_duration_minutes`
- Status tracking and timestamps

**4. Survey Templates**
- Versioned survey definitions per organization
- Fields: `name`, `description`, `questions` (JSONB), `triggers` (JSONB), `delivery_settings` (JSONB)
- Metadata: `active`, `version`, `created_by` (FK to USERS), timestamps

**5. Feedback Sessions**
- Individual survey instances triggered by appointments
- Tracking: `completion_token` (unique), session timing (`initiated_at`, `first_response_at`, `completed_at`, `expired_at`)
- Delivery: `delivery_method`, `delivery_attempts`, `last_delivery_attempt`
- Analytics: `ip_address`, `user_agent`, `completion_time_seconds`

**6. Feedback Response Types**
- Catalog of allowable response formats
- Examples: yes_no, rating_scale, text_input, multiple_choice
- Fields: `type_name`, `type_category`, `validation_rules` (JSONB), `display_options` (JSONB)

**7. Feedback Responses**
- Individual answers within feedback sessions
- Fields: `question_id`, `response_value` (JSONB), `response_text`, `ai_analysis` (JSONB)
- Performance tracking: `response_time_seconds`

### Relationship Flow
1. **Organization** → **Users** (providers, patients, admins)
2. **Users** → **Appointments** (patients attend, providers conduct)
3. **Appointments** → **Feedback Sessions** (trigger surveys)
4. **Survey Templates** → **Feedback Sessions** (define structure)
5. **Feedback Sessions** → **Feedback Responses** (collect answers)
6. **Response Types** → **Responses** (define format/validation)

This design supports multi-tenant healthcare organizations collecting patient feedback through configurable surveys triggered by appointment events.