# Survey Collection System API Routes - MVP

This document provides a comprehensive overview of all API routes for the MVP version of the survey collection system.

## Overview

The MVP API provides a streamlined set of endpoints for healthcare survey management in a multi-tenant system. Admins create surveys while providers (doctors) can view survey results and analytics.

## Access Summary Table
| Route Group         | Path Prefix            | Who Can Access?                | Key Permissions / Notes                    |
|---------------------|-----------------------|-------------------------------|--------------------------------------------|
| Organizations       | `/organizations`      | Superuser (full), Admins (read own) | Superuser: full CRUD; Admins: view their own org only |
| Survey Templates    | `/survey-templates`   | Admins (full), Providers (read) | Admins: create/update/delete; Providers: read-only |
| Feedback Sessions   | `/feedback-sessions`  | Admins (full), Providers (read), Public (by token) | Admins: create/update/delete; Providers: read-only; Public: access by session token |
| Items               | `/items`              | Superuser (all), User (own)   | Superuser: all items; User: own items only |
| Users               | `/users`              | Superuser                     | Full user management                       |
| Login/Auth          | `/login`              | All (public)                  | Token-based authentication                 |

**Legend**:  
- **Superuser**: Platform-level admin  
- **Admin**: Organization admin  
- **Provider**: Doctor/healthcare provider  
- **User**: Regular user (e.g., survey respondent)  
- **Public**: No authentication required (e.g., via token link)


## Authentication & Authorization

- **JWT-based authentication** with access and refresh tokens
- **Role-based access control**:
  - **Admins**: Full survey management (create, update, delete surveys and sessions)
  - **Providers (Doctors)**: Read-only access to view surveys, responses, and analytics
  - **Survey Respondents**: Public access via completion tokens (no authentication required)
- **Multi-tenant isolation**: Users can only access data within their organization

## API Route Groups

### 1. Organizations (`/organizations`)

Multi-tenant organization management (superuser access required for most operations).

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/organizations/` | List all organizations | Superuser only |
| `POST` | `/organizations/` | Create new organization | Superuser only |
| `GET` | `/organizations/me` | Get current user's organization | Organization members (read-only) |
| `GET` | `/organizations/{id}` | Get organization by ID | Organization members (read-only) + Superusers |
| `PATCH` | `/organizations/{id}` | Update organization | Superuser only |
| `DELETE` | `/organizations/{id}` | Delete organization (cascade) | Superuser only |

### 2. Survey Templates (`/survey-templates`)

Configurable survey template management with JSONB question storage.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/survey-templates/` | List organization's templates | Admins + Providers |
| `POST` | `/survey-templates/` | Create new template | Admins only |
| `GET` | `/survey-templates/active` | List active templates only | Admins + Providers |
| `GET` | `/survey-templates/{id}` | Get template by ID | Admins + Providers |
| `PATCH` | `/survey-templates/{id}` | Update template | Admins only |
| `DELETE` | `/survey-templates/{id}` | Delete template | Admins only |
| `POST` | `/survey-templates/{id}/duplicate` | Duplicate template | Admins only |
| `PATCH` | `/survey-templates/{id}/activate` | Activate template | Admins only |
| `PATCH` | `/survey-templates/{id}/deactivate` | Deactivate template | Admins only |

### 3. Feedback Sessions (`/feedback-sessions`)

Survey session management with token-based respondent access.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/feedback-sessions/` | List feedback sessions | Admins + Providers |
| `POST` | `/feedback-sessions/` | Create new session | Admins only |
| `GET` | `/feedback-sessions/by-token/{token}` | Get session by token | Public (for survey respondents) |
| `GET` | `/feedback-sessions/{id}` | Get session by ID | Admins + Providers |
| `PATCH` | `/feedback-sessions/{id}` | Update session | Admins only |
| `PATCH` | `/feedback-sessions/by-token/{token}` | Update session by token | Public (for respondent interactions) |
| `DELETE` | `/feedback-sessions/{id}` | Delete session | Admins only |
| `PATCH` | `/feedback-sessions/{id}/complete` | Mark session complete | Admins only |
| `PATCH` | `/feedback-sessions/by-token/{token}/complete` | Complete by token | Public |
| `GET` | `/feedback-sessions/stats/organization` | Organization statistics | Admins + Providers |

### 4. Feedback Responses (`/feedback-responses`)

Individual survey response management with analytics.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/feedback-responses/` | List responses | Admins + Providers |
| `POST` | `/feedback-responses/` | Create single response | Public (for survey respondents) |
| `POST` | `/feedback-responses/batch` | Create multiple responses | Public (for survey respondents) |
| `GET` | `/feedback-responses/session/{session_id}` | Get responses by session | Admins + Providers |
| `GET` | `/feedback-responses/{id}` | Get response by ID | Admins + Providers |
| `PATCH` | `/feedback-responses/{id}` | Update response | Admins only |
| `DELETE` | `/feedback-responses/{id}` | Delete response | Admins only |
| `GET` | `/feedback-responses/analytics/question/{question_id}` | Question analytics | Admins + Providers |

### 5. Feedback Response Types (`/feedback-response-types`)

Question type catalog management (system-wide, managed by superusers).

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/feedback-response-types/` | List active response types | All users |
| `GET` | `/feedback-response-types/all` | List all response types | All users (inactive: Admins only) |
| `POST` | `/feedback-response-types/` | Create response type | Superuser only |
| `GET` | `/feedback-response-types/{id}` | Get response type by ID | All users (inactive: Admins only) |
| `GET` | `/feedback-response-types/by-name/{name}` | Get by name | All users (inactive: Admins only) |
| `GET` | `/feedback-response-types/by-category/{category}` | Get by category | All users |
| `PATCH` | `/feedback-response-types/{id}` | Update response type | Superuser only |
| `DELETE` | `/feedback-response-types/{id}` | Delete response type | Superuser only |
| `PATCH` | `/feedback-response-types/{id}/activate` | Activate response type | Superuser only |
| `PATCH` | `/feedback-response-types/{id}/deactivate` | Deactivate response type | Superuser only |

### 6. Users (`/users`) - Enhanced

Existing user management with healthcare-specific fields and multi-tenant support.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/users/` | List all users | Superuser only |
| `POST` | `/users/` | Create new user | Superuser only |
| `POST` | `/users/signup` | User self-registration | Public |
| `GET` | `/users/me` | Get current user profile | Authenticated users |
| `PATCH` | `/users/me` | Update own profile | Authenticated users |
| `PATCH` | `/users/me/password` | Update own password | Authenticated users |
| `DELETE` | `/users/me` | Delete own account | Authenticated users |
| `GET` | `/users/{id}` | Get user by ID | User themselves + Superusers |
| `PATCH` | `/users/{id}` | Update user | Superuser only |
| `DELETE` | `/users/{id}` | Delete user | Superuser only |

### 7. Authentication (`/login`)

JWT-based authentication system.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/login/access-token` | Login and get access token | Public |
| `POST` | `/login/test-token` | Test token validity | Authenticated users |
| `POST` | `/login/recover-password` | Request password reset | Public |
| `POST` | `/login/reset-password` | Reset password with token | Public |

## Key Features

### Multi-Tenant Architecture
- All data is scoped to organizations
- Users can only access data within their organization
- Superusers can manage multiple organizations

### Role-Based Access Control
- **Superusers**: Platform-level access (manage organizations, full system access)
- **Admins**: Organization-level management (create, update, delete surveys and sessions within their org)
- **Providers (Doctors)**: Read-only access to view surveys, responses, and analytics within their org
- **Survey Respondents**: Public access to complete surveys via completion tokens (no authentication required)

### Survey System
- **Configurable Templates**: JSONB-based flexible question definitions
- **Token-Based Access**: Secure survey links for respondents
- **Response Tracking**: Detailed analytics and completion tracking
- **Multi-Channel Delivery**: Support for email, SMS, phone, and in-person
- **Appointment-Independent**: Surveys can be created and managed independently of appointments for MVP simplicity

### Security Features
- JWT authentication with refresh tokens
- Encrypted PII fields (phone numbers, emails)
- Organization-scoped data access
- Input validation with Pydantic models
- SQL injection protection with SQLModel

### Analytics & Reporting
- Organization-wide feedback statistics
- Question-level response analytics
- Completion rate tracking
- Response time analysis

## Data Flow Example (MVP)

1. **Admin** creates a survey template with questions
2. **Admin** creates a feedback session (independent of appointments)
3. **Survey respondent** receives survey link with completion token
4. **Survey respondent** accesses survey using token (no authentication required)
5. **Survey respondent** submits responses (batch or individual)
6. **Admin/Provider** reviews responses and analytics
7. **Admin/Provider** views organization-wide statistics

## Error Handling

All routes include comprehensive error handling:
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `409`: Conflict (duplicate resources)
- `410`: Gone (expired resources, like survey sessions)

## Response Formats

All routes return consistent JSON responses:
- Single resources: `{resource_data}`
- Collections: `{data: [resources], count: total_count}`
- Success messages: `{message: "Operation completed"}`
- Errors: `{detail: "Error description"}`

## Next Steps

The MVP API is ready for:
1. **Frontend Integration**: All endpoints support the React/TypeScript frontend
2. **Mobile Apps**: RESTful design suitable for mobile clients
3. **Analytics Dashboard**: Statistics endpoints support real-time reporting
4. **Notification Services**: Session management supports email/SMS triggers
5. **Future Expansion**: Easy to add appointment integration when needed

## MVP Benefits

- **Clear Role Separation**: Admins manage, providers view, respondents participate
- **Provider Access**: Doctors can view survey results and analytics for their organization
- **Simplified Management**: Admin-only creation reduces complexity while maintaining provider visibility
- **Core Functionality**: Focus on essential survey features with proper access control
- **Easy Migration**: Data model supports future appointment integration
- **Public Survey Access**: Token-based system works without authentication

## Access Summary

| User Type | Manage Organizations | Create Surveys | View Surveys | View Responses | View Analytics | Manage Sessions |
|-----------|---------------------|----------------|--------------|----------------|----------------|-----------------|
| **Superuser** | ✅ (Full CRUD) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Admin** | ❌ (View own only) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Provider (Doctor)** | ❌ (View own only) | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Survey Respondent** | ❌ | ❌ | ❌ (via token) | ❌ (create only) | ❌ | ❌ |