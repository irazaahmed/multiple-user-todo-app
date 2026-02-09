# Tasks: Backend Foundation

**Input**: Design documents from `/specs/001-backend-foundation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not requested in feature specification. Manual testing with curl/Postman per spec.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` at repository root
- Routes in `backend/routes/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [X] T001 Create backend directory structure with `backend/`, `backend/routes/`, `backend/__init__.py`, `backend/routes/__init__.py`
- [X] T002 Create `backend/requirements.txt` with pinned dependencies: fastapi==0.115.0, uvicorn[standard]==0.32.0, sqlmodel==0.0.22, psycopg2-binary==2.9.10, python-dotenv==1.0.1, pydantic==2.10.0
- [X] T003 [P] Create `backend/.env.example` with DATABASE_URL and CORS_ORIGINS placeholders and documentation comments
- [X] T004 [P] Add `backend/.env` to `.gitignore` to prevent secrets from being committed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create User SQLModel in `backend/models.py` with id (UUID, PK, default uuid4), email (str, unique, index, max 255), password_hash (str, max 255), name (Optional[str], max 255), created_at (datetime), updated_at (datetime), and tasks relationship (Ref: data-model.md User entity, FR-001)
- [X] T006 Create Task SQLModel in `backend/models.py` with id (Optional[int], PK), user_id (UUID, FK users.id, index), title (str, max 200), description (Optional[str]), completed (bool, default False), created_at (datetime), updated_at (datetime), and user relationship. Add index on completed and created_at (Ref: data-model.md Task entity, FR-002, FR-003, FR-004)
- [X] T007 Create database connection module `backend/db.py` with DATABASE_URL from env var, create_engine with pool_size=20, max_overflow=10, pool_pre_ping=True, init_db() function calling SQLModel.metadata.create_all, and get_session() generator yielding Session for FastAPI Depends (Ref: research.md decisions 3, 7; FR-019)
- [X] T008 [P] Create Pydantic schemas in `backend/schemas.py`: TaskCreate (title: str min 1 max 200, description: Optional[str] max 1000), TaskUpdate (title: Optional[str] min 1 max 200, description: Optional[str] max 1000), TaskResponse (id, user_id, title, description, completed, created_at, updated_at with model_config ConfigDict from_attributes=True) (Ref: contracts/openapi.yaml schemas, FR-014, FR-015)

**Checkpoint**: Foundation ready - models, database connection, and schemas available for all user stories

---

## Phase 3: User Story 1 - Application Startup & Health (Priority: P1) MVP

**Goal**: Running FastAPI application connected to Neon PostgreSQL with health endpoint

**Independent Test**: Start server, call `GET /health`, verify `{"status": "ok", "database": "connected"}`

### Implementation for User Story 1

- [X] T009 [US1] Create FastAPI application in `backend/main.py` with lifespan context manager that calls init_db() on startup, configure CORSMiddleware reading CORS_ORIGINS from env var (split on comma), allow methods=["*"] and headers=["*"] (Ref: research.md decisions 1, 6; FR-019, FR-020)
- [X] T010 [US1] Implement GET /health endpoint in `backend/main.py` that queries database with `SELECT 1` to verify connectivity and returns `{"status": "ok", "database": "connected"}` with 200, or `{"detail": "Database connection failed", "status_code": 500}` on failure (Ref: contracts/openapi.yaml /health, FR-018)
- [X] T011 [US1] Include task router in `backend/main.py` with `app.include_router(router, prefix="/api/v1")` importing from `backend/routes/tasks.py` (Ref: plan.md Phase 5)
- [X] T012 [US1] Load environment variables using python-dotenv in `backend/main.py` by calling `load_dotenv()` before app creation (Ref: constitution Principle II - all secrets via env vars)

**Checkpoint**: Application starts, connects to Neon database, tables created, health endpoint returns 200

---

## Phase 4: User Story 2 - Create Task (Priority: P1) MVP

**Goal**: Users can create tasks via POST endpoint with validation

**Independent Test**: `curl -X POST /api/v1/{user_id}/tasks -d '{"title":"Test"}' → 201 with task JSON`

### Implementation for User Story 2

- [X] T013 [US2] Implement POST `/{user_id}/tasks` endpoint in `backend/routes/tasks.py` that validates user_id as UUID, creates Task with user_id from path and fields from TaskCreate body, commits to database, returns 201 with TaskResponse and Location header (Ref: contracts/openapi.yaml POST /tasks, FR-005, FR-011)

**Checkpoint**: Tasks can be created for a user and persisted to database

---

## Phase 5: User Story 3 - View All Tasks (Priority: P1) MVP

**Goal**: Users can list their own tasks with optional status filtering

**Independent Test**: Create tasks, `curl GET /api/v1/{user_id}/tasks → 200 with array of user's tasks only`

### Implementation for User Story 3

- [X] T014 [US3] Implement GET `/{user_id}/tasks` endpoint in `backend/routes/tasks.py` that queries tasks filtered by user_id, supports optional `?status=pending|completed|all` query parameter, orders by created_at DESC, returns 200 with List[TaskResponse] or empty array [] (Ref: contracts/openapi.yaml GET /tasks, FR-006, FR-011, data-model.md query patterns)

**Checkpoint**: User sees only their tasks, filtering works, empty list for new users

---

## Phase 6: User Story 4 - View Single Task (Priority: P2)

**Goal**: Users can retrieve a specific task by ID with data isolation

**Independent Test**: `curl GET /api/v1/{user_id}/tasks/{id} → 200 with task or 404`

### Implementation for User Story 4

- [X] T015 [US4] Implement GET `/{user_id}/tasks/{task_id}` endpoint in `backend/routes/tasks.py` that queries by BOTH task_id AND user_id (data isolation), returns 200 with TaskResponse if found, raises HTTPException 404 with detail "Task not found" if not found or belongs to different user (Ref: contracts/openapi.yaml GET /tasks/{id}, FR-007, FR-011, FR-012)

**Checkpoint**: Single task retrieval works with data isolation enforced

---

## Phase 7: User Story 5 - Update Task (Priority: P2)

**Goal**: Users can update task title and/or description

**Independent Test**: `curl -X PUT /api/v1/{user_id}/tasks/{id} -d '{"title":"New"}' → 200 with updated task`

### Implementation for User Story 5

- [X] T016 [US5] Implement PUT `/{user_id}/tasks/{task_id}` endpoint in `backend/routes/tasks.py` that queries task by task_id AND user_id, raises 404 if not found, applies non-None fields from TaskUpdate body, sets updated_at to datetime.utcnow(), commits and returns 200 with updated TaskResponse (Ref: contracts/openapi.yaml PUT /tasks/{id}, FR-008, FR-011, FR-012, data-model.md update pattern)

**Checkpoint**: Tasks can be updated with partial fields, timestamp refreshed

---

## Phase 8: User Story 6 - Delete Task (Priority: P2)

**Goal**: Users can permanently delete their own tasks

**Independent Test**: `curl -X DELETE /api/v1/{user_id}/tasks/{id} → 204 No Content`

### Implementation for User Story 6

- [X] T017 [US6] Implement DELETE `/{user_id}/tasks/{task_id}` endpoint in `backend/routes/tasks.py` that queries task by task_id AND user_id, raises 404 if not found, calls session.delete(task), commits, returns Response with status_code=204 (Ref: contracts/openapi.yaml DELETE /tasks/{id}, FR-009, FR-011, FR-012)

**Checkpoint**: Tasks deleted permanently, 404 for non-existent or other user's tasks

---

## Phase 9: User Story 7 - Toggle Completion (Priority: P2)

**Goal**: Users can toggle task completion status (pending/completed)

**Independent Test**: `curl -X PATCH /api/v1/{user_id}/tasks/{id}/complete → 200 with toggled completed field`

### Implementation for User Story 7

- [X] T018 [US7] Implement PATCH `/{user_id}/tasks/{task_id}/complete` endpoint in `backend/routes/tasks.py` that queries task by task_id AND user_id, raises 404 if not found, toggles task.completed with `not` operator, sets updated_at to datetime.utcnow(), commits and returns 200 with updated TaskResponse (Ref: contracts/openapi.yaml PATCH /complete, FR-010, FR-011, FR-012, data-model.md toggle pattern)

**Checkpoint**: Completion toggles correctly, timestamp updated, data isolation enforced

---

## Phase 10: User Story 8 - Validation & Error Handling (Priority: P3)

**Goal**: All endpoints return proper error responses for invalid input

**Independent Test**: Send invalid data to each endpoint, verify 400/404/422/500 responses with clear messages

### Implementation for User Story 8

- [X] T019 [US8] Add UUID validation for user_id path parameter across all routes in `backend/routes/tasks.py` by using `UUID` type annotation on user_id parameter; FastAPI auto-returns 422 for invalid UUIDs, add custom exception handler in `backend/main.py` to convert to 400 with `{"detail": "Invalid user_id format", "status_code": 400}` (Ref: FR-013, FR-016, edge case: invalid UUID format)
- [X] T020 [US8] Add global exception handler in `backend/main.py` for database errors (SQLAlchemyError) that returns 500 with `{"detail": "Internal server error", "status_code": 500}` without exposing stack traces (Ref: FR-017, edge case: database connection failure)

**Checkpoint**: All error scenarios return correct status codes with clear messages, no stack traces exposed

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final verification

- [X] T021 Create `backend/README.md` with setup instructions, environment variables, how to run server, API endpoint documentation with curl examples (Ref: quickstart.md)
- [X] T022 Verify all endpoints with curl: create test user via SQL, test POST/GET/GET-single/PUT/DELETE/PATCH for happy paths (Ref: quickstart.md test commands)
- [X] T023 Verify data isolation: create two users, create tasks for each, confirm User A cannot see/modify User B's tasks (Ref: FR-011, FR-012, SC-004, SC-005)
- [X] T024 Verify validation: test missing title (422), title >200 chars (422), description >1000 chars (422), invalid UUID (400), non-existent task (404) (Ref: FR-014, FR-015, FR-016)
- [X] T025 Add type hints to all function parameters and return values in all backend files, verify with mypy (Ref: constitution Principle III - Type Safety)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **US1 App Startup (Phase 3)**: Depends on Phase 2 - BLOCKS US2-US8 (app must run first)
- **US2 Create (Phase 4)**: Depends on Phase 3 (needs running app with router)
- **US3 List (Phase 5)**: Depends on Phase 3 (needs running app)
- **US4 Get Single (Phase 6)**: Depends on Phase 3
- **US5 Update (Phase 7)**: Depends on Phase 3
- **US6 Delete (Phase 8)**: Depends on Phase 3
- **US7 Toggle (Phase 9)**: Depends on Phase 3
- **US8 Error Handling (Phase 10)**: Depends on Phases 4-9 (needs all endpoints to exist)
- **Polish (Phase 11)**: Depends on all story phases complete

### Within Each User Story

- All routes are in the same file (`backend/routes/tasks.py`), so phases 4-9 are sequential
- Each endpoint builds on the shared models, schemas, and session dependency from Phase 2

### Parallel Opportunities

- Phase 1: T003 and T004 can run in parallel
- Phase 2: T005+T006 (models.py) are sequential, T007 (db.py) and T008 (schemas.py) can run in parallel after models
- Phases 4-9: US2 through US7 endpoints can conceptually run in parallel BUT share routes/tasks.py, so sequencing is recommended to avoid conflicts

---

## Parallel Example: Phase 2

```bash
# After T005+T006 (models.py) complete:
Task T007: "Create database connection module in backend/db.py"       # parallel
Task T008: "Create Pydantic schemas in backend/schemas.py"            # parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008)
3. Complete Phase 3: US1 App Startup (T009-T012)
4. Complete Phase 4: US2 Create Task (T013)
5. Complete Phase 5: US3 List Tasks (T014)
6. **STOP and VALIDATE**: App runs, tasks can be created and listed
7. Deploy/demo if ready

### Full Delivery

1. Complete MVP (Phases 1-5)
2. Add US4-US7 (Phases 6-9) → Complete CRUD
3. Add US8 (Phase 10) → Error handling polished
4. Polish (Phase 11) → Documentation and verification

---

## Notes

- All routes are in single file `backend/routes/tasks.py` for simplicity
- Models (User, Task) are in single file `backend/models.py` per plan
- No test tasks generated (manual testing per spec)
- Commit after each task: `T-XXX: <description>` per constitution
- Every query in routes/tasks.py MUST include `Task.user_id == user_id` filter
