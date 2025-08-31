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
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- Git

### Quick Start

#### Option 1: Full Docker Setup (Recommended for Quick Testing)

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd survey-collection
```

2. **Start everything with Docker:**
```bash
# Start all services (database, backend, frontend)
docker compose watch
```

3. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database Admin (Adminer): http://localhost:8080
- Traefik Dashboard: http://localhost:8090

**Note:** First startup may take 2-3 minutes while services initialize.

#### Option 2: Local Development Setup (Recommended for Development)

1. **Clone and setup environment:**
```bash
git clone <your-repo-url>
cd survey-collection

# Create environment file (if .env.example doesn't exist, create .env manually)
cp .env.example .env || echo "Create .env file with database settings (see troubleshooting section)"
```

2. **Setup Python backend:**
```bash
# Install dependencies with uv (creates venv automatically)
cd backend
uv sync
cd ..
```

3. **Setup frontend:**
```bash
cd frontend
npm install
cd ..
```

4. **Start services separately:**
```bash
# Terminal 1: Start the application
docker compose up

# Terminal 2: Start backend (uv automatically activates venv)
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev
```

5. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Workflow

**Backend Development:**
```bash
cd backend

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name
```

**Alternative: Run backend with Docker (no uv needed):**
```bash
# Start backend with database
docker compose up -d
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

### Python Dependency Management with uv

**Why use uv?**
- **Fast**: 10-100x faster than pip for dependency resolution and installation
- **Reliable**: Consistent dependency resolution with lockfile support
- **Simple**: Automatic virtual environment management
- **Compatible**: Drop-in replacement for pip and pip-tools

**Managing Dependencies:**
```bash
cd backend

# Install all dependencies (creates .venv automatically)
uv sync

# Add new runtime dependency
uv add fastapi

# Add new development dependency
uv add --dev pytest

# Remove dependency
uv remove package-name

# Update dependencies
uv sync --upgrade

# Run commands in the virtual environment
uv run python script.py
uv run pytest
uv run alembic upgrade head
```

**uv Tips:**
- Virtual environment is created automatically in `.venv/`
- No need to manually activate/deactivate - `uv run` handles it
- `uv.lock` file ensures reproducible installs across environments
- Use `uv sync` after pulling changes to update dependencies
- Add `.venv/` to `.gitignore` (already included)

### Troubleshooting

**"Address already in use" Error:**
```bash
# Check what's running on port 8000
lsof -i :8000

# Kill process using port 8000 (replace PID with actual process ID)
kill -9 <PID>

# Or stop all Docker containers
docker compose down

# Then restart your development server
```

**Database Connection Issues:**
```bash
# Ensure PostgreSQL is running
docker compose up -d db

# Check database logs
docker compose logs db

# Reset database (caution: deletes all data)
docker compose down -v
docker compose up -d db
```

**Environment Variables Missing:**
```bash
# If you see environment variable errors, create .env file manually
cat > .env << 'EOF'
# Basic configuration for local development
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5173
ENVIRONMENT=local
SECRET_KEY=your-super-secret-key-change-this
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=survey_collection
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis123
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis123
DOCKER_IMAGE_BACKEND=survey-collection-backend
DOCKER_IMAGE_FRONTEND=survey-collection-frontend
TAG=latest
STACK_NAME=survey-collection
EOF
```

**Frontend Not Starting:**
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**uv Build Errors (httptools, uvloop on macOS):**
```bash
# Option 1: Install build dependencies
brew install python-setuptools

# Option 2: Use pre-built wheels (if available)
cd backend
uv sync --no-build

# Option 3: Skip problematic packages temporarily
cd backend
uv sync --no-build-isolation

# Option 4: For Apple Silicon Macs, ensure correct architecture
export ARCHFLAGS="-arch arm64"  # For M1/M2 Macs
# or
export ARCHFLAGS="-arch x86_64"  # For Intel Macs
uv sync

# Option 5: Use system Python if homebrew Python causes issues
uv sync --python $(which python3)
```

**Python Version Issues:**
```bash
# Check Python version (should be 3.10-3.12 for best compatibility)
python --version

# Use specific Python version with uv
uv sync --python 3.11

# If using Python 3.13, some packages might not have wheels yet
# Consider using Python 3.11 or 3.12 instead
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
uv run pytest

# Backend tests with coverage
uv run coverage run -m pytest
uv run coverage report

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
