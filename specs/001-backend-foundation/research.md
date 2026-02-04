# Research: Backend Foundation

**Feature**: 001-backend-foundation
**Date**: 2026-02-04
**Status**: Complete

## Technology Decisions

### 1. FastAPI Framework Configuration

**Decision**: Use FastAPI 0.115.0 with lifespan context manager for startup/shutdown events

**Rationale**:
- Lifespan context manager is the modern approach (replaces deprecated @app.on_event)
- Enables clean database initialization on startup
- Provides graceful shutdown handling
- Built-in async support for future enhancements

**Alternatives Considered**:
- @app.on_event("startup") - Deprecated in FastAPI, avoid for new code
- Flask - Does not meet constitution requirements (FastAPI mandated)
- Django - Does not meet constitution requirements (FastAPI mandated)

### 2. SQLModel ORM Pattern

**Decision**: Use SQLModel 0.0.22 with table=True for database models, separate Pydantic schemas for API validation

**Rationale**:
- SQLModel combines SQLAlchemy and Pydantic in one class
- Setting table=True creates database table definition
- Separate Pydantic schemas allow different validation rules for create/update/response
- Relationships defined using Relationship() with back_populates for bidirectional access

**Alternatives Considered**:
- Raw SQLAlchemy - Constitution mandates SQLModel exclusively
- Django ORM - Constitution prohibits non-FastAPI frameworks
- Tortoise ORM - Not in approved tech stack

### 3. Database Connection Pooling

**Decision**: Use SQLModel/SQLAlchemy engine with pool_size=20, max_overflow=10, pool_pre_ping=True

**Rationale**:
- pool_size=20 handles normal concurrent load (constitution specifies max 20 connections)
- max_overflow=10 allows burst capacity without permanent connection growth
- pool_pre_ping=True validates connections before use (handles Neon serverless cold starts)
- Synchronous engine for simplicity in Phase 2 (async can be added later)

**Alternatives Considered**:
- No pooling - Would create new connection per request, inefficient and slow
- Async engine - Adds complexity without immediate benefit for this spec
- Larger pool - Exceeds constitution constraint of 20 connections

### 4. UUID vs Serial Primary Keys

**Decision**: Users use UUID primary key, Tasks use SERIAL (auto-increment integer)

**Rationale**:
- User UUID enables distributed ID generation (required for Better Auth integration in Spec 2)
- Task SERIAL is simpler and more performant for single-database operations
- Task.user_id as UUID foreign key enforces referential integrity
- Mixed approach balances requirements and performance

**Alternatives Considered**:
- UUID for both - Unnecessary complexity for tasks, larger storage
- SERIAL for both - Would conflict with Better Auth user ID requirements
- ULID - Not widely supported in Python ecosystem

### 5. Error Response Format

**Decision**: Use HTTPException with detail field, status_code in response body

**Rationale**:
- FastAPI's HTTPException provides consistent error handling
- detail field matches spec requirement for clear error messages
- Adding status_code in body matches constitution format: {"detail": "message", "status_code": XXX}
- Validation errors automatically return 422 with field-specific messages

**Alternatives Considered**:
- Custom exception classes - Unnecessary complexity for this scope
- Plain dict responses - Loses HTTPException benefits (proper status codes)

### 6. CORS Configuration

**Decision**: Parse CORS_ORIGINS from environment variable, split on comma, configure middleware

**Rationale**:
- Environment variable allows different origins for dev/staging/production
- Comma-separated format is simple to configure
- FastAPI CORSMiddleware handles preflight requests automatically
- Allow all methods and headers for API flexibility

**Alternatives Considered**:
- Hardcoded origins - Violates constitution (all config via env vars)
- Wildcard (*) - Security risk, disabled in production
- JSON array in env var - More complex to parse

### 7. Timestamp Auto-Population

**Decision**: Use default_factory=datetime.utcnow for created_at, manual update for updated_at in route handlers

**Rationale**:
- SQLModel/SQLAlchemy default_factory runs on INSERT
- Manual updated_at assignment ensures it only changes on actual updates
- UTC timestamps avoid timezone confusion
- Consistent with spec requirement for automatic timestamp management

**Alternatives Considered**:
- Database triggers - Adds database-level complexity
- SQLAlchemy onupdate - Requires additional configuration
- Client-provided timestamps - Security risk, clients shouldn't control this

## Best Practices Applied

### Data Isolation Pattern

All task queries MUST include user_id filter:
```python
# Correct: Always filter by user_id
statement = select(Task).where(Task.user_id == user_id)

# Incorrect: Never query without user_id
statement = select(Task).where(Task.id == task_id)  # SECURITY RISK
```

### 404 for Access Denied

Return 404 (not 403) when accessing another user's task:
```python
# Returns 404 whether task doesn't exist OR belongs to different user
task = session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

This prevents information disclosure (attacker can't determine if task ID exists).

### Dependency Injection for Sessions

Use FastAPI Depends for database sessions:
```python
def get_session():
    with Session(engine) as session:
        yield session

@router.get("/{user_id}/tasks")
def get_tasks(user_id: UUID, session: Session = Depends(get_session)):
    ...
```

Benefits:
- Automatic session cleanup on request completion
- Testable (can mock session in tests)
- Consistent session handling across all routes

## Unresolved Items

None. All technical decisions resolved for this spec. JWT authentication deferred to Spec 2.
