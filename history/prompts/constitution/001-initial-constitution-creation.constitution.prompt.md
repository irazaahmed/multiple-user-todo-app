---
id: 001
title: Initial Constitution Creation for Multi-User Todo App
stage: constitution
date: 2026-02-01
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "project-setup", "governance", "full-stack"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution

Project: Phase 2 - Full-Stack Multi-User Todo Web Application

Core principles:
- Spec-Driven Development: No code written without corresponding specification and task
- Security-first design: User data isolation enforced at all layers
- Type safety: Strong typing in both frontend (TypeScript) and backend (Python type hints)
- Stateless architecture: API must be horizontally scalable without session state
- Single source of truth: Database is the only persistent state store

Key standards:
- Tech Stack Lock (Non-Negotiable):
  * Frontend: Next.js 16+ with App Router (no Pages Router)
  * Backend: FastAPI with Python 3.13+
  * Database: Neon Serverless PostgreSQL
  * ORM: SQLModel exclusively (no raw SQLAlchemy or other ORMs)
  * Authentication: Better Auth with JWT tokens
  * Deployment: Vercel (frontend), Railway/Render (backend)

- Code Quality Standards:
  * TypeScript strict mode enabled for all frontend code
  * Python type hints mandatory for all functions and variables
  * Async/await for all I/O operations (database queries, API calls)
  * Pydantic models for all API request/response validation
  * Zero tolerance for hardcoded credentials or secrets
  * All configuration via environment variables

- API Design Standards:
  * RESTful conventions strictly followed
  * Base path: /api/v1/{user_id}/resource
  * HTTP status codes: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 422 (Validation Error), 500 (Server Error)
  * Consistent error response format: {"detail": "message", "status_code": XXX}
  * All endpoints require JWT authentication
  * JSON responses only (no HTML, XML, or other formats)

- Security Standards:
  * JWT tokens with 7-day expiry
  * BETTER_AUTH_SECRET minimum 32 characters, stored in environment variables
  * User can ONLY access their own data (strict user_id filtering on all queries)
  * Password hashing with bcrypt (minimum cost factor 12)
  * CORS configured to allow only trusted frontend origins
  * SQL injection prevention via parameterized queries (SQLModel ORM)
  * XSS prevention via proper input sanitization

- Database Standards:
  * Every table with user-scoped data MUST have user_id foreign key
  * All tables MUST have created_at and updated_at timestamps
  * Indexes on foreign keys and frequently queried columns
  * Soft deletes preferred over hard deletes (use deleted_at column)
  * Database migrations must be reversible
  * Connection pooling enabled (max 20 connections)

- Development Workflow Standards:
  * Specify → Plan → Tasks → Implement (no deviation)
  * Each task must reference spec sections
  * Each commit must reference task ID (e.g., "T-005: Implement JWT middleware")
  * Backend endpoints tested with Postman/curl before frontend integration
  * No manual coding - all implementation via Claude Code

Constraints:
- Technology Constraints:
  * No Python frameworks other than FastAPI
  * No React frameworks other than Next.js 16+
  * No ORMs other than SQLModel
  * No authentication libraries other than Better Auth
  * No CSS frameworks other than Tailwind CSS

- Data Constraints:
  * Maximum task title length: 200 characters
  * Maximum task description length: 1000 characters
  * Maximum tasks per user: 1000 (soft limit)
  * JWT token expiry: exactly 7 days
  * Minimum password length: 8 characters

- Architecture Constraints:
  * Monorepo structure (frontend and backend in same repository)
  * Frontend and backend must run independently
  * No shared code between frontend and backend (except types)
  * Stateless API (no server-side sessions)
  * Database is single source of truth (no caching layer in Phase 2)

- Deployment Constraints:
  * Frontend must deploy to Vercel
  * Backend must deploy to Railway or Render
  * Database must be Neon Serverless PostgreSQL
  * All secrets managed via platform environment variables
  * HTTPS required in production

Success criteria:
- Functional Requirements:
  * All 5 basic features implemented: Add, Delete, Update, View, Mark Complete
  * User authentication working (signup, login, logout)
  * Multi-user data isolation verified (User A cannot see User B's tasks)
  * All 6 API endpoints functional and returning correct status codes
  * Frontend communicates with backend via authenticated API calls
  * Tasks persist across browser sessions

- Security Requirements:
  * JWT verification working on all protected endpoints
  * Invalid/expired tokens rejected with 401
  * User_id mismatch returns 403
  * No user can access another user's data
  * Passwords never stored in plaintext
  * No secrets committed to git repository

- Quality Requirements:
  * Zero TypeScript errors in frontend build
  * Zero Python type checking errors (mypy pass)
  * All API endpoints tested and documented
  * Frontend builds successfully without warnings
  * Backend passes health check
  * Database schema matches specification exactly

- Deployment Requirements:
  * Frontend accessible via public Vercel URL
  * Backend accessible via public Railway/Render URL
  * Database accessible from backend
  * CORS configured correctly (no errors in browser console)
  * Environment variables properly configured
  * Demo video under 90 seconds demonstrating all features

- Documentation Requirements:
  * README.md with setup instructions
  * API documentation with request/response examples
  * Environment variables documented in .env.example
  * All specs (constitution, specify, plan, tasks) committed to repo
  * AGENTS.md and CLAUDE.md in repository root

## Response snapshot

Created project constitution v1.0.0 with 6 core principles:
1. Spec-Driven Development (NON-NEGOTIABLE)
2. Security-First Design (NON-NEGOTIABLE)
3. Type Safety
4. Stateless Architecture
5. Single Source of Truth
6. RESTful API Standards

Additional sections: Technology Standards (with non-negotiable tech stack), Development Workflow Standards, Constraints (data and architecture), Success Criteria (functional, security, quality, deployment, documentation), and Governance.

## Outcome

- Impact: Created foundational governance document establishing all project principles, standards, and success criteria
- Tests: N/A (constitution document)
- Files: 1 created (.specify/memory/constitution.md)
- Next prompts: /sp.specify to create feature specification for the todo application
- Reflection: Comprehensive constitution captures all user requirements with clear NON-NEGOTIABLE markers

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): standard-constitution
- Next experiment: Monitor adherence during implementation phase
