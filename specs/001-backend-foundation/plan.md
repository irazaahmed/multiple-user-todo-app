# Implementation Plan: Backend Foundation

**Branch**: `001-backend-foundation` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-foundation/spec.md`

## Summary

Build the FastAPI backend foundation with SQLModel ORM connecting to Neon Serverless PostgreSQL. Implements complete CRUD operations for tasks with strict user data isolation, request/response validation via Pydantic schemas, and health check endpoint. All database queries filter by user_id from URL path to enforce multi-user data separation.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI 0.115.0, SQLModel 0.0.22, Pydantic 2.10.0, Uvicorn 0.32.0, psycopg2-binary 2.9.10
**Storage**: Neon Serverless PostgreSQL with connection pooling (pool_size=20, max_overflow=10)
**Testing**: Manual testing with curl/Postman (automated tests deferred to later phase)
**Target Platform**: Linux server (Railway/Render deployment)
**Project Type**: Web application (backend only in this spec)
**Performance Goals**: <200ms response time for typical CRUD operations, <500ms health check
**Constraints**: Max 200 char title, max 1000 char description, max 1000 tasks per user
**Scale/Scope**: Multi-user task management, 6 API endpoints + 1 health endpoint

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | Spec created first (spec.md), plan follows spec, tasks will reference spec sections |
| II. Security-First Design | PASS | All queries filter by user_id, 404 returned for other users' data (not 403), no hardcoded secrets |
| III. Type Safety | PASS | Python type hints on all functions, Pydantic models for validation |
| IV. Stateless Architecture | PASS | No server-side sessions, user_id from URL path, stateless API design |
| V. Single Source of Truth | PARTIAL | Using hard delete (soft delete deferred per spec assumptions), timestamps on all tables |
| VI. RESTful API Standards | PASS | Base path /api/v1/{user_id}/tasks, correct HTTP status codes, JSON responses only |

**Tech Stack Compliance**:
- Backend Framework: FastAPI (COMPLIANT)
- ORM: SQLModel (COMPLIANT)
- Database: Neon Serverless PostgreSQL (COMPLIANT)

**Gate Status**: PASS (soft delete deviation documented in spec assumptions as acceptable for Phase 2)

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - API contracts
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── checklists/
    └── requirements.md  # Spec validation checklist
```

### Source Code (repository root)

```text
backend/
├── __init__.py          # Package marker
├── main.py              # FastAPI app entry point, CORS, health endpoint
├── models.py            # SQLModel User and Task models
├── db.py                # Database connection, session management
├── schemas.py           # Pydantic request/response schemas
├── routes/
│   ├── __init__.py      # Routes package marker
│   └── tasks.py         # Task CRUD endpoints
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md            # Backend setup documentation
```

**Structure Decision**: Web application backend structure selected. Frontend will be added in Spec 3 under `frontend/` directory. Backend is self-contained with clear separation: models (data), schemas (validation), routes (endpoints), db (connection).

## Complexity Tracking

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Hard delete instead of soft delete | Simplifies Phase 2 implementation | Soft delete adds complexity without immediate benefit; can be added in later phase |

## Implementation Phases

### Phase 1: Project Setup
- Create backend/ directory structure
- Initialize requirements.txt with pinned dependencies
- Create .env.example with documented placeholders
- Verify Python 3.13+ available

### Phase 2: Database Models
- Implement User SQLModel with UUID primary key
- Implement Task SQLModel with foreign key to User
- Define bidirectional relationships
- Add indexes on user_id, completed, created_at

### Phase 3: Database Connection
- Create db.py with engine configuration
- Implement connection pooling (20 connections, 10 overflow)
- Create init_db() for table creation
- Create get_session() dependency for routes

### Phase 4: Pydantic Schemas
- TaskCreate schema with title (required), description (optional)
- TaskUpdate schema with optional fields
- TaskResponse schema matching Task model
- Validation constraints: title 1-200 chars, description max 1000 chars

### Phase 5: FastAPI Application
- Create app with lifespan context manager
- Configure CORS from environment variable
- Implement /health endpoint
- Register task routes with prefix

### Phase 6: Task CRUD Routes
- GET /{user_id}/tasks - List with optional status filter
- POST /{user_id}/tasks - Create with 201 response
- GET /{user_id}/tasks/{id} - Get single with 404 handling
- PUT /{user_id}/tasks/{id} - Update with validation
- DELETE /{user_id}/tasks/{id} - Delete with 204 response
- PATCH /{user_id}/tasks/{id}/complete - Toggle completion

### Phase 7: Testing & Verification
- Test all endpoints with curl/Postman
- Verify data isolation between users
- Test validation error responses
- Verify health endpoint connectivity

## Dependencies

```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlmodel==0.0.22
psycopg2-binary==2.9.10
python-dotenv==1.0.1
pydantic==2.10.0
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DATABASE_URL | Yes | Neon PostgreSQL connection string | postgresql://user:pass@host.neon.tech:5432/db |
| CORS_ORIGINS | Yes | Comma-separated allowed origins | http://localhost:3000 |

## Success Verification

- [ ] GET /health returns 200 with {"status": "ok", "database": "connected"}
- [ ] All 6 task endpoints respond with correct status codes
- [ ] User A cannot see/modify User B's tasks (returns 404)
- [ ] Validation errors return 422 with field details
- [ ] Invalid UUID returns 400 Bad Request
- [ ] Database connection pooling active
