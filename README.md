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

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Quick Start

1. **Clone and setup the project:**
```bash
git clone <your-repo-url>
cd survey-collection
```

2. **Start the development environment:**
```bash
# Start database and backend
docker-compose up -d

# Install frontend dependencies and start dev server
cd frontend
npm install
npm run dev
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: PostgreSQL on localhost:5432

### Development Workflow

**Backend Development:**
```bash
cd backend
# Install dependencies
pip install -e .
# Run database migrations
alembic upgrade head
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**
```bash
cd frontend
# Start development server
npm run dev
# Run tests
npm test
# Build for production
npm run build
```

## 📊 Data Model

The system uses a unified data model with the following core entities:

- **Organizations**: Multi-tenant containers
- **Users**: Unified table for providers, patients, and admins (with `user_type` field)
- **Appointments**: Patient-provider encounters
- **Survey Templates**: Configurable survey definitions (JSONB)
- **Feedback Sessions**: Individual survey instances
- **Feedback Responses**: Patient answers and analytics
- **Response Types**: Question type catalog

See [design/data-model.md](design/data-model.md) for detailed entity relationships.

## 📚 Documentation

- [System Architecture](design/architecture.md) - High-level system design
- [Data Model](design/data-model.md) - Database schema and relationships
- [Development Guide](development.md) - Development setup and guidelines
- [Deployment Guide](deployment.md) - Production deployment instructions

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 🔒 Security Features

- **Multi-tenant data isolation** - Organization-scoped queries
- **Encrypted PII** - Phone numbers and emails encrypted at rest
- **JWT Authentication** - Access and refresh token rotation
- **Role-based permissions** - Provider, patient, and admin roles
- **Input validation** - Comprehensive Pydantic validation
- **HTTPS ready** - SSL/TLS configuration for production

## 🚀 Future Enhancements

### Planned Features
- **EHR Integration**: HL7 FHIR APIs for appointment synchronization
- **Advanced Analytics**: Real-time dashboards and reporting
- **AI Analysis**: Sentiment analysis and automated insights
- **Mobile Apps**: Native iOS/Android applications
- **Multi-channel Delivery**: SMS, phone, and in-person kiosks

### Scaling Considerations
- Load balancer (Nginx/Traefik) for multiple backend instances
- Redis caching layer for improved performance
- Read replicas for analytics queries
- Microservices architecture for large-scale deployments

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]