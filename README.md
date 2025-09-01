# Survey Collection System

A multi-tenant healthcare application that collects patient feedback through configurable surveys after medical appointments. Built with React/TypeScript frontend and FastAPI backend.

## 🏥 Business Overview

This system enables healthcare organizations to systematically collect and analyze patient feedback following appointments. It provides a structured approach to patient experience measurement with role-based access for providers, patients, and administrators.

### Target Users
- **Healthcare Organizations**: Hospitals, clinics, and medical practices
- **Healthcare Providers**: Doctors, nurses, and clinical staff
- **Patients**: Individuals receiving medical care
- **Administrators**: Quality improvement and patient experience teams

## 🚀 Key Features (MVP)

- **Multi-Tenant Architecture**: Support for multiple healthcare organizations
- **Unified User Management**: Providers, patients, and admins in single user model
- **Configurable Surveys**: JSONB-based survey templates with flexible question types
- **Automated Survey Delivery**: Email and SMS notifications post-appointment
- **Appointment Integration**: Ready for EHR system integration
- **Secure Data Handling**: Encrypted PII fields and organization-scoped data
- **Role-Based Access**: Different permissions for providers, patients, and admins

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   (TypeScript)  │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Notification  │    │   File Storage  │
                       │   Services      │    │   (Local FS)    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   EHR Systems   │
                       │   (Future)      │
                       └─────────────────┘
```

## 📁 Project Structure

```
survey-collection/
├── frontend/                    # React/TypeScript application
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── routes/            # Page routes
│   │   ├── hooks/             # Custom React hooks
│   │   └── client/            # Generated API client
│   ├── tests/                 # Frontend tests
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration and security
│   │   ├── models.py          # Database models
│   │   └── crud.py            # Database operations
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── pyproject.toml
├── design/                      # Design documents
│   ├── architecture.md        # System architecture
│   └── data-model.md          # Database design
├── scripts/                     # Utility scripts
└── docker-compose.yml          # Local development setup
```

## 🛠️ Technology Stack

### Frontend
- **React 18+** with TypeScript
- **TanStack Router** for routing
- **TanStack Query** for API state management
- **Chakra UI** for component library
- **React Hook Form** with Zod validation
- **Vite** for build tooling

### Backend
- **FastAPI** with Python 3.11+
- **SQLAlchemy 2.0** (async) with PostgreSQL
- **Alembic** for database migrations
- **Pydantic v2** for data validation
- **JWT** authentication with refresh tokens
- **FastAPI BackgroundTasks** for async operations

### Database & Storage
- **PostgreSQL 15+** for all application data:
  - Organizations (multi-tenant container)
  - Users (providers, patients, admins)
  - Appointments and clinical data
  - Survey templates and responses
  - Feedback sessions and analytics
- **Local filesystem** for file storage

### Development & Deployment
- **Docker & Docker Compose** for containerization
- **pytest** for backend testing
- **Vitest & Playwright** for frontend testing

## 🚀 Getting Started

### Prerequisites

- 🐳 [Docker](https://www.docker.com/) and Docker Compose
- 🐍 Python 3.10+
- 📦 Node.js 18+ with npm
- 🔧 [uv](https://docs.astral.sh/uv/) for Python package management (backend)
- 🔧 [nvm](https://github.com/nvm-sh/nvm) for Node version management (frontend)

### 🏃‍♂️ Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/feedback-collection.git
   cd feedback-collection
   ```

2. **Start docker**

   ```bash
   docker compose up -d
   ```

3. **Run database migrations**

   ```bash
   docker compose exec backend alembic upgrade head
   ```

## 🛠️ Development

### Backend Development

   ```bash
   cd backend
   uv sync
   source .venv/bin/activate
   ```

### Frontend Development

   ```bash
   cd frontend
   npm install
   npm run dev
   ```


### 🔄 Database Migrations

**Create a new migration** (after modifying models):

```bash
docker compose exec backend alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:

```bash
docker compose exec backend alembic upgrade head
```

### 📝 API Client Generation

When backend API changes, regenerate the frontend client:

```bash
# From project root
./scripts/generate-client.sh
```

Or manually:

```bash
cd frontend
npm run generate-client
```

## 📊 Data Model

The system uses the following key entities:

- **Users**: With roles (doctor, patient, admin)
- **Hospitals**: Healthcare facilities
- **SurveyCampaigns**: Feedback campaigns per hospital
- **Questions**: Survey questions with types (rating, yes/no, free_form)
- **PatientVisits**: Records of patient visits
- **QuestionResponses**: Patient feedback responses

See [patient-feedback-data-model.md](./patient-feedback-data-model.md) for detailed documentation.

## 🔐 Security

### Environment Variables

**Generate secure keys**:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Critical variables to change**:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

### API Security

- JWT-based authentication
- Role-based access control (RBAC)
- Secure password hashing (bcrypt)
- CORS configuration

## 📦 Deployment

See [deployment.md](./deployment.md) for detailed deployment instructions.

### Quick Production Setup

1. **Update `.env` for production**
2. **Build and start services**:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```
