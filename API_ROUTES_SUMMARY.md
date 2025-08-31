# Survey Collection System API Routes

This document provides a comprehensive overview of all API routes created for the survey collection system.

## Overview

The API provides a complete set of endpoints for managing a multi-tenant healthcare survey collection system. The routes are organized into logical groups with proper authentication, authorization, and multi-tenant data isolation.

## Authentication & Authorization

- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** with three user types:
  - `ADMIN`: Full access within their organization
  - `PROVIDER`: Limited access to their patients and appointments
  - `PATIENT`: Access to their own data only
- **Multi-tenant isolation**: Users can only access data within their organization

## API Route Groups

### 1. Organizations (`/organizations`)

Multi-tenant organization management (superuser access required for most operations).

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/organizations/` | List all organizations | Superuser only |
| `POST` | `/organizations/` | Create new organization | Superuser only |
| `GET` | `/organizations/me` | Get current user's organization | Authenticated users |
| `GET` | `/organizations/{id}` | Get organization by ID | Organization members + superusers |
| `PATCH` | `/organizations/{id}` | Update organization | Superuser only |
| `DELETE` | `/organizations/{id}` | Delete organization (cascade) | Superuser only |

### 2. Appointments (`/appointments`)

Healthcare appointment management with role-based access.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/appointments/` | List appointments | Role-based filtering |
| `POST` | `/appointments/` | Create new appointment | Providers + Admins |
| `GET` | `/appointments/{id}` | Get appointment by ID | Involved parties + Admins |
| `PATCH` | `/appointments/{id}` | Update appointment | Providers + Admins |
| `DELETE` | `/appointments/{id}` | Delete appointment | Providers + Admins |
| `GET` | `/appointments/patient/{patient_id}` | Get patient's appointments | Patient + their providers + Admins |
| `GET` | `/appointments/provider/{provider_id}` | Get provider's appointments | Provider + Admins |

### 3. Survey Templates (`/survey-templates`)

Configurable survey template management with JSONB question storage.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/survey-templates/` | List organization's templates | Organization members |
| `POST` | `/survey-templates/` | Create new template | Providers + Admins |
| `GET` | `/survey-templates/active` | List active templates only | Organization members |
| `GET` | `/survey-templates/{id}` | Get template by ID | Organization members |
| `PATCH` | `/survey-templates/{id}` | Update template | Creator + Admins |
| `DELETE` | `/survey-templates/{id}` | Delete template | Creator + Admins |
| `POST` | `/survey-templates/{id}/duplicate` | Duplicate template | Providers + Admins |
| `PATCH` | `/survey-templates/{id}/activate` | Activate template | Creator + Admins |
| `PATCH` | `/survey-templates/{id}/deactivate` | Deactivate template | Creator + Admins |

### 4. Feedback Sessions (`/feedback-sessions`)

Survey session management with token-based patient access.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/feedback-sessions/` | List feedback sessions | Role-based filtering |
| `POST` | `/feedback-sessions/` | Create new session | Providers + Admins |
| `GET` | `/feedback-sessions/by-appointment/{appointment_id}` | Get session by appointment | Involved parties + Admins |
| `GET` | `/feedback-sessions/by-token/{token}` | Get session by token | Public (for patient surveys) |
| `GET` | `/feedback-sessions/{id}` | Get session by ID | Involved parties + Admins |
| `PATCH` | `/feedback-sessions/{id}` | Update session | Providers + Admins |
| `PATCH` | `/feedback-sessions/by-token/{token}` | Update session by token | Public (for patient responses) |
| `DELETE` | `/feedback-sessions/{id}` | Delete session | Admins only |
| `PATCH` | `/feedback-sessions/{id}/complete` | Mark session complete | Involved parties + Admins |
| `PATCH` | `/feedback-sessions/by-token/{token}/complete` | Complete by token | Public |
| `GET` | `/feedback-sessions/stats/organization` | Organization statistics | Admins only |

### 5. Feedback Responses (`/feedback-responses`)

Individual survey response management with analytics.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/feedback-responses/` | List responses | Role-based filtering |
| `POST` | `/feedback-responses/` | Create single response | Involved parties + Admins |
| `POST` | `/feedback-responses/batch` | Create multiple responses | Involved parties + Admins |
| `GET` | `/feedback-responses/session/{session_id}` | Get responses by session | Involved parties + Admins |
| `GET` | `/feedback-responses/{id}` | Get response by ID | Involved parties + Admins |
| `PATCH` | `/feedback-responses/{id}` | Update response | Providers + Admins |
| `DELETE` | `/feedback-responses/{id}` | Delete response | Admins only |
| `GET` | `/feedback-responses/analytics/question/{question_id}` | Question analytics | Admins only |

### 6. Feedback Response Types (`/feedback-response-types`)

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

### 7. Users (`/users`) - Enhanced

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

### 8. Authentication (`/login`)

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
- **Patients**: Can view their appointments and complete surveys
- **Providers**: Can manage their patients' appointments and surveys
- **Admins**: Full access within their organization
- **Superusers**: System-wide access

### Survey System
- **Configurable Templates**: JSONB-based flexible question definitions
- **Token-Based Access**: Secure survey links for patients
- **Response Tracking**: Detailed analytics and completion tracking
- **Multi-Channel Delivery**: Support for email, SMS, phone, and in-person

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

## Data Flow Example

1. **Provider** creates an appointment for a **Patient**
2. **Admin/Provider** creates a feedback session linked to the appointment
3. **Patient** receives survey link with completion token
4. **Patient** accesses survey using token (no authentication required)
5. **Patient** submits responses (batch or individual)
6. **Provider/Admin** reviews responses and analytics
7. **Admin** views organization-wide statistics

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

The API is ready for:
1. **Frontend Integration**: All endpoints support the React/TypeScript frontend
2. **Mobile Apps**: RESTful design suitable for mobile clients
3. **EHR Integration**: Appointment endpoints ready for HL7 FHIR integration
4. **Analytics Dashboard**: Statistics endpoints support real-time reporting
5. **Notification Services**: Session management supports email/SMS triggers
