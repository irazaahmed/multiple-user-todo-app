<!--
  ==================== SYNC IMPACT REPORT ====================
  Version Change: N/A → 1.0.0 (Initial creation)

  Modified Principles: N/A (Initial creation)

  Added Sections:
    - Core Principles (6 principles)
    - Technology Standards
    - Development Workflow Standards
    - Constraints
    - Success Criteria
    - Governance

  Removed Sections: N/A

  Templates Requiring Updates:
    - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
    - .specify/templates/spec-template.md: ✅ Compatible (Requirements align with principles)
    - .specify/templates/tasks-template.md: ✅ Compatible (Phase structure supports workflow)

  Follow-up TODOs: None
  =============================================================
-->

# Full-Stack Multi-User Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

No code written without corresponding specification and task. The development workflow MUST follow the strict sequence: Specify → Plan → Tasks → Implement with no deviation permitted.

- Each task MUST reference spec sections explicitly
- Each commit MUST reference task ID (e.g., "T-005: Implement JWT middleware")
- Backend endpoints MUST be tested with Postman/curl before frontend integration
- All implementation MUST be executed via Claude Code (no manual coding)

**Rationale**: Ensures traceability, prevents scope creep, and maintains alignment between requirements and implementation.

### II. Security-First Design (NON-NEGOTIABLE)

User data isolation MUST be enforced at all layers. Security is not an afterthought but a foundational requirement.

- User can ONLY access their own data (strict user_id filtering on ALL queries)
- JWT tokens with 7-day expiry; BETTER_AUTH_SECRET minimum 32 characters
- Password hashing with bcrypt (minimum cost factor 12)
- CORS configured to allow only trusted frontend origins
- SQL injection prevention via parameterized queries (SQLModel ORM)
- XSS prevention via proper input sanitization
- Zero tolerance for hardcoded credentials or secrets
- All secrets stored in environment variables

**Rationale**: Multi-user applications require strict data isolation; security breaches have severe consequences.

### III. Type Safety

Strong typing in both frontend (TypeScript) and backend (Python type hints) is mandatory.

- TypeScript strict mode MUST be enabled for all frontend code
- Python type hints MUST be present on all functions and variables
- Pydantic models MUST be used for all API request/response validation
- Zero TypeScript errors permitted in frontend build
- Zero Python type checking errors permitted (mypy pass required)

**Rationale**: Type safety catches errors at compile time, improves maintainability, and serves as documentation.

### IV. Stateless Architecture

API MUST be horizontally scalable without session state.

- No server-side sessions permitted
- All state MUST be transmitted via JWT tokens
- Each request MUST be self-contained
- No in-memory caching of user state
- Async/await MUST be used for all I/O operations (database queries, API calls)

**Rationale**: Enables horizontal scaling, simplifies deployment, and improves reliability.

### V. Single Source of Truth

Database is the only persistent state store.

- No caching layer in Phase 2 (database is authoritative)
- All tables MUST have created_at and updated_at timestamps
- Every table with user-scoped data MUST have user_id foreign key
- Soft deletes preferred over hard deletes (use deleted_at column)
- Database migrations MUST be reversible
- Connection pooling enabled (max 20 connections)

**Rationale**: Eliminates consistency issues between multiple data stores and simplifies debugging.

### VI. RESTful API Standards

All API endpoints MUST follow RESTful conventions strictly.

- Base path: `/api/v1/{user_id}/resource`
- HTTP status codes: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 422 (Validation Error), 500 (Server Error)
- Consistent error response format: `{"detail": "message", "status_code": XXX}`
- All endpoints MUST require JWT authentication
- JSON responses only (no HTML, XML, or other formats)

**Rationale**: Consistent API design improves developer experience and reduces integration errors.

## Technology Standards

### Tech Stack (NON-NEGOTIABLE)

| Layer | Technology | Version/Notes |
|-------|------------|---------------|
| Frontend Framework | Next.js with App Router | 16+ (no Pages Router) |
| Backend Framework | FastAPI | Python 3.13+ |
| Database | Neon Serverless PostgreSQL | Hosted |
| ORM | SQLModel | Exclusively (no raw SQLAlchemy) |
| Authentication | Better Auth | JWT tokens |
| CSS Framework | Tailwind CSS | Latest stable |
| Frontend Deployment | Vercel | Required |
| Backend Deployment | Railway or Render | Required |

### Prohibited Technologies

- No Python frameworks other than FastAPI
- No React frameworks other than Next.js 16+
- No ORMs other than SQLModel
- No authentication libraries other than Better Auth
- No CSS frameworks other than Tailwind CSS

### Code Quality Standards

- All configuration via environment variables
- Indexes on foreign keys and frequently queried columns
- All API endpoints tested and documented
- Frontend builds successfully without warnings
- Backend passes health check

## Development Workflow Standards

### Mandatory Sequence

1. **Specify**: Create feature specification from requirements
2. **Plan**: Design architecture and technical approach
3. **Tasks**: Generate actionable, dependency-ordered task list
4. **Implement**: Execute tasks in order, referencing specs

### Commit Standards

- Format: `T-XXX: <description>` where XXX is the task ID
- Each commit MUST reference exactly one task
- No commits without corresponding task

### Testing Protocol

- Backend endpoints tested with Postman/curl before frontend integration
- Integration tests for user data isolation
- API documentation with request/response examples

## Constraints

### Data Constraints

| Constraint | Value |
|------------|-------|
| Maximum task title length | 200 characters |
| Maximum task description length | 1000 characters |
| Maximum tasks per user | 1000 (soft limit) |
| JWT token expiry | 7 days (exactly) |
| Minimum password length | 8 characters |

### Architecture Constraints

- Monorepo structure (frontend and backend in same repository)
- Frontend and backend MUST run independently
- No shared code between frontend and backend (except types)
- HTTPS required in production

## Success Criteria

### Functional Requirements

- [ ] All 5 basic features implemented: Add, Delete, Update, View, Mark Complete
- [ ] User authentication working (signup, login, logout)
- [ ] Multi-user data isolation verified (User A cannot see User B's tasks)
- [ ] All 6 API endpoints functional and returning correct status codes
- [ ] Frontend communicates with backend via authenticated API calls
- [ ] Tasks persist across browser sessions

### Security Requirements

- [ ] JWT verification working on all protected endpoints
- [ ] Invalid/expired tokens rejected with 401
- [ ] User_id mismatch returns 403
- [ ] No user can access another user's data
- [ ] Passwords never stored in plaintext
- [ ] No secrets committed to git repository

### Quality Requirements

- [ ] Zero TypeScript errors in frontend build
- [ ] Zero Python type checking errors (mypy pass)
- [ ] All API endpoints tested and documented
- [ ] Frontend builds successfully without warnings
- [ ] Backend passes health check
- [ ] Database schema matches specification exactly

### Deployment Requirements

- [ ] Frontend accessible via public Vercel URL
- [ ] Backend accessible via public Railway/Render URL
- [ ] Database accessible from backend
- [ ] CORS configured correctly (no errors in browser console)
- [ ] Environment variables properly configured
- [ ] Demo video under 90 seconds demonstrating all features

### Documentation Requirements

- [ ] README.md with setup instructions
- [ ] API documentation with request/response examples
- [ ] Environment variables documented in .env.example
- [ ] All specs (constitution, specify, plan, tasks) committed to repo
- [ ] AGENTS.md and CLAUDE.md in repository root

## Governance

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Changes affecting security principles require explicit security review
3. Version bump follows semantic versioning:
   - **MAJOR**: Backward incompatible principle removal or redefinition
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes

### Compliance

- All PRs/reviews MUST verify compliance with this constitution
- Complexity additions MUST be justified in PR description
- Use `CLAUDE.md` for runtime development guidance
- Constitution supersedes all other project practices

**Version**: 1.0.0 | **Ratified**: 2026-02-01 | **Last Amended**: 2026-02-01
