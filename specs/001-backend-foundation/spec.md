# Feature Specification: Backend Foundation (Database + Models + REST API)

**Feature Branch**: `001-backend-foundation`
**Created**: 2026-02-04
**Status**: Draft
**Input**: Phase 2, Spec 1 - Backend Foundation for multi-user task management system

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Application Startup and Health Verification (Priority: P1)

A developer sets up the backend application and verifies it connects to the database correctly. The developer configures environment variables, starts the server, and confirms the system is ready to accept requests via a health check endpoint.

**Why this priority**: Foundation for all other functionality. Without a running, database-connected backend, no other features can work.

**Independent Test**: Can be fully tested by starting the application and calling the health endpoint. Delivers immediate feedback on system readiness.

**Acceptance Scenarios**:

1. **Given** DATABASE_URL and CORS_ORIGINS environment variables are set, **When** the application starts, **Then** it connects to the database and creates tables if they don't exist
2. **Given** the application is running, **When** a client calls the health endpoint, **Then** it returns a success status confirming database connectivity
3. **Given** DATABASE_URL is missing or invalid, **When** the application attempts to start, **Then** it fails with a clear error message

---

### User Story 2 - Create a New Task (Priority: P1)

A user wants to create a new task in their personal task list. They send their user identifier and task details (title and optional description) to the system, which stores the task and returns the created task with a unique identifier.

**Why this priority**: Core CRUD operation. Creating tasks is the fundamental action users need to manage their to-do lists.

**Independent Test**: Can be fully tested by sending a create request with valid data and verifying the response contains the created task with all fields populated.

**Acceptance Scenarios**:

1. **Given** a valid user identifier and task title, **When** a create request is sent, **Then** the system stores the task and returns it with a unique ID, timestamps, and default completion status (false)
2. **Given** a valid user identifier, title, and description, **When** a create request is sent, **Then** the task is created with all provided fields
3. **Given** a request without a title, **When** the create request is sent, **Then** the system returns a validation error with specific field details
4. **Given** a title exceeding 200 characters, **When** the create request is sent, **Then** the system returns a validation error

---

### User Story 3 - View All Tasks (Priority: P1)

A user wants to see all their tasks to understand what they need to do. They request their task list and receive all tasks they've created, without seeing other users' tasks.

**Why this priority**: Users must be able to view their data. This also validates the critical data isolation requirement.

**Independent Test**: Can be fully tested by creating tasks for a user, then retrieving them. Verifying empty response for users with no tasks.

**Acceptance Scenarios**:

1. **Given** a user with multiple tasks, **When** they request their task list, **Then** they receive all their tasks ordered by creation date (newest first)
2. **Given** a user with no tasks, **When** they request their task list, **Then** they receive an empty list (not an error)
3. **Given** two different users with their own tasks, **When** User A requests their task list, **Then** they only see their own tasks (not User B's)
4. **Given** a user wants to see only pending tasks, **When** they request with a status filter, **Then** they receive only incomplete tasks

---

### User Story 4 - View Single Task (Priority: P2)

A user wants to view the details of a specific task. They request a task by its identifier and receive the full task details if it belongs to them.

**Why this priority**: Required for task detail views and before performing updates.

**Independent Test**: Can be fully tested by creating a task, then retrieving it by ID.

**Acceptance Scenarios**:

1. **Given** a user owns a task with a specific ID, **When** they request that task, **Then** they receive the complete task details
2. **Given** a task does not exist, **When** a user requests it, **Then** they receive a "not found" response
3. **Given** a task belongs to a different user, **When** a user tries to access it, **Then** they receive a "not found" response (data isolation)

---

### User Story 5 - Update Task Details (Priority: P2)

A user wants to modify their task's title or description. They send updated information for a specific task, and the system persists the changes.

**Why this priority**: Essential for correcting mistakes or refining task details.

**Independent Test**: Can be fully tested by creating a task, updating it, and verifying the changes persist.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** they send updated title/description, **Then** the task is updated and the modification timestamp is refreshed
2. **Given** an update with an empty title, **When** submitted, **Then** the system returns a validation error
3. **Given** a task belonging to another user, **When** update is attempted, **Then** the system returns "not found" (data isolation)

---

### User Story 6 - Delete Task (Priority: P2)

A user wants to remove a task they no longer need. They request deletion of a specific task, and the system removes it permanently.

**Why this priority**: Users need to clean up completed or unwanted tasks.

**Independent Test**: Can be fully tested by creating a task, deleting it, then verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** they request its deletion, **Then** the task is removed and no content is returned
2. **Given** a task does not exist, **When** deletion is requested, **Then** "not found" is returned
3. **Given** a task belongs to another user, **When** deletion is attempted, **Then** "not found" is returned (data isolation)

---

### User Story 7 - Toggle Task Completion (Priority: P2)

A user wants to mark a task as complete or incomplete. They toggle the completion status of a specific task, and the system updates it accordingly.

**Why this priority**: Core functionality for task management - tracking what's done vs. pending.

**Independent Test**: Can be fully tested by creating a task, toggling it complete, then toggling again to incomplete.

**Acceptance Scenarios**:

1. **Given** an incomplete task, **When** the user toggles completion, **Then** the task becomes complete and the modification timestamp is refreshed
2. **Given** a completed task, **When** the user toggles completion, **Then** the task becomes incomplete
3. **Given** a task belonging to another user, **When** toggle is attempted, **Then** "not found" is returned (data isolation)

---

### User Story 8 - Validation Error Handling (Priority: P3)

When a user submits invalid data, the system provides clear, actionable feedback about what's wrong so they can correct their input.

**Why this priority**: Good error messages improve user experience and reduce confusion.

**Independent Test**: Can be tested by submitting various invalid inputs and verifying error responses contain specific field-level guidance.

**Acceptance Scenarios**:

1. **Given** a request missing required fields, **When** submitted, **Then** the error response identifies which fields are missing
2. **Given** a request with fields exceeding length limits, **When** submitted, **Then** the error response identifies which fields are too long
3. **Given** malformed request data, **When** submitted, **Then** a parsing error is returned
4. **Given** an invalid user identifier format, **When** any request is made, **Then** a "bad request" error is returned

---

### Edge Cases

- What happens when a user identifier is not a valid UUID format? → Return 400 Bad Request
- What happens when database connection fails during a request? → Return 500 Internal Server Error without exposing internal details
- What happens when a task's description is exactly 1000 characters? → Accept (at boundary)
- What happens when a task's title is exactly 200 characters? → Accept (at boundary)
- What happens when updating with only description (no title change)? → Accept partial update
- What happens when task ID doesn't exist AND user ID doesn't exist? → Return 404 (don't reveal which is invalid)
- What happens with concurrent modifications to the same task? → Last write wins (standard database behavior)

## Requirements *(mandatory)*

### Functional Requirements

**Database & Data Storage**

- **FR-001**: System MUST store users with unique identifier, email (unique), password hash, name, and automatic timestamps
- **FR-002**: System MUST store tasks with unique identifier, owner reference, title (max 200 chars), description (max 1000 chars), completion status, and automatic timestamps
- **FR-003**: System MUST automatically remove all tasks when their owner is deleted (cascading delete)
- **FR-004**: System MUST optimize task queries by owner, completion status, and creation date

**Task CRUD Operations**

- **FR-005**: System MUST allow creating a task with title (required) and description (optional)
- **FR-006**: System MUST allow retrieving all tasks for a specific user with optional completion status filter
- **FR-007**: System MUST allow retrieving a single task by its identifier
- **FR-008**: System MUST allow updating a task's title and/or description
- **FR-009**: System MUST allow deleting a task
- **FR-010**: System MUST allow toggling a task's completion status

**Data Isolation & Security**

- **FR-011**: System MUST filter ALL task operations by the requesting user's identifier
- **FR-012**: System MUST return "not found" (not "forbidden") when accessing another user's task to prevent information disclosure
- **FR-013**: System MUST validate user identifier format before processing any request

**Validation & Error Handling**

- **FR-014**: System MUST validate task title is present and between 1-200 characters
- **FR-015**: System MUST validate task description does not exceed 1000 characters when provided
- **FR-016**: System MUST return field-specific validation errors with clear messages
- **FR-017**: System MUST NOT expose internal error details or stack traces in error responses

**Health & Connectivity**

- **FR-018**: System MUST provide a health check endpoint that verifies database connectivity
- **FR-019**: System MUST fail startup if database connection cannot be established
- **FR-020**: System MUST allow requests from configured frontend origins (CORS)

### Key Entities

- **User**: Represents a registered user of the system. Has unique identifier (UUID), email (unique), password hash (for authentication), display name, and timestamps for creation and last modification. Owns zero or more tasks.

- **Task**: Represents a to-do item belonging to a user. Has unique identifier (serial number), owner reference (UUID), title (required, max 200 chars), description (optional, max 1000 chars), completion flag (boolean), and timestamps for creation and last modification. Belongs to exactly one user.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Functionality**

- **SC-001**: All 6 task operations (list, create, get, update, delete, toggle) successfully execute and return appropriate responses
- **SC-002**: Users can create, view, update, delete, and complete tasks within 2 seconds per operation under normal load
- **SC-003**: Task list filtering by status returns accurate results (only pending OR only completed tasks)

**Data Isolation**

- **SC-004**: 100% of task queries return only data belonging to the requesting user
- **SC-005**: Attempting to access another user's task returns "not found" in 100% of cases (verified by cross-user testing)

**Validation**

- **SC-006**: 100% of invalid inputs return clear, field-specific error messages
- **SC-007**: Title validation rejects 100% of empty titles and titles exceeding 200 characters
- **SC-008**: Description validation rejects 100% of descriptions exceeding 1000 characters

**Reliability**

- **SC-009**: Health check endpoint confirms database connectivity within 500ms
- **SC-010**: System gracefully handles database connection failures with appropriate error responses (no crashes, no exposed internals)

**Integration Readiness**

- **SC-011**: All endpoints accept and return data in the documented format for frontend integration
- **SC-012**: CORS configuration allows requests from the configured frontend origin

## Assumptions

- User identifiers are UUIDs provided in the URL path (authentication/authorization will be added in Spec 2)
- Task IDs are auto-incrementing integers (serial)
- The system uses environment variables for all configuration (DATABASE_URL, CORS_ORIGINS)
- Connection pooling parameters: 20 connections max, 10 overflow, with pre-ping enabled for stale connection handling
- Tasks are ordered by creation date descending (newest first) by default
- "Soft delete" mentioned in constitution will be implemented in a later phase; this spec uses hard delete for simplicity
- Password hashing is handled by Better Auth (Spec 2), not this spec

## Out of Scope

- JWT authentication middleware (Spec 2)
- User signup/login endpoints (Spec 2 with Better Auth)
- Frontend UI components (Spec 3)
- WebSocket real-time updates
- Task filtering by date ranges or tags
- Task priority or category fields
- File attachments or images
- Task sharing between users
- Email notifications
- Rate limiting or throttling
- API documentation UI (Swagger/ReDoc)
