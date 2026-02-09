# Feature Specification: Authentication & Security

**Feature Branch**: `002-authentication-security`
**Created**: 2026-02-09
**Status**: Draft
**Input**: Spec 2 - Authentication & Security with Better Auth (Next.js), JWT plugin, FastAPI middleware

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Signup (Priority: P1)

A new user visits the application and creates an account by providing their email address and a password. The system validates the input, securely stores the credentials, and provides the user with an authenticated session.

**Why this priority**: Without signup, no users can exist in the system. This is the entry point for all user interactions and enables all subsequent authentication flows.

**Independent Test**: Can be fully tested by submitting a signup form with valid credentials and verifying the user can immediately access their empty task list.

**Acceptance Scenarios**:

1. **Given** a visitor on the signup page, **When** they provide a valid email and password (8+ characters), **Then** an account is created and they receive a valid authentication token
2. **Given** a visitor attempts signup, **When** they provide an email that already exists, **Then** they receive an error message indicating the email is taken
3. **Given** a visitor attempts signup, **When** they provide a password shorter than 8 characters, **Then** they receive a validation error with specific guidance
4. **Given** a visitor attempts signup, **When** they provide an invalid email format, **Then** they receive a validation error indicating the email is invalid

---

### User Story 2 - Existing User Login (Priority: P1)

A registered user returns to the application and authenticates using their email and password. Upon successful authentication, they receive a token that grants access to their protected resources.

**Why this priority**: Login is essential for returning users to access their data. Combined with signup, this completes the core authentication cycle.

**Independent Test**: Can be fully tested by logging in with valid credentials and verifying the user receives a token that can be used to access protected endpoints.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page, **When** they provide correct email and password, **Then** they receive a valid JWT token with 7-day expiry
2. **Given** a user attempts login, **When** they provide incorrect password, **Then** they receive a generic "invalid credentials" error (no indication which field is wrong)
3. **Given** a user attempts login, **When** they provide a non-existent email, **Then** they receive the same generic "invalid credentials" error
4. **Given** a user has logged in, **When** they check their token, **Then** it contains their user_id and expiration timestamp

---

### User Story 3 - Authenticated API Request (Priority: P1)

An authenticated user makes a request to a protected endpoint (e.g., list tasks). The system validates their JWT token and ensures they can only access their own data.

**Why this priority**: This is the core security mechanism that protects all task operations. Without this, the existing task API would be unprotected.

**Independent Test**: Can be fully tested by making API requests with a valid token and verifying access, then making the same request without a token and verifying rejection.

**Acceptance Scenarios**:

1. **Given** an authenticated user with valid JWT, **When** they request their tasks, **Then** they receive only their own tasks
2. **Given** an authenticated user, **When** their JWT includes user_id "A" but they request tasks for user_id "B" in the URL, **Then** they receive a 403 Forbidden error
3. **Given** a request without any JWT token, **When** sent to a protected endpoint, **Then** it receives a 401 Unauthorized error
4. **Given** an authenticated user, **When** they successfully access a protected endpoint, **Then** the response time is not significantly impacted by token verification (under 50ms added latency)

---

### User Story 4 - Expired Token Handling (Priority: P2)

A user's JWT token expires after 7 days. When they attempt to use an expired token, the system rejects it and guides them to re-authenticate.

**Why this priority**: Token expiration is a critical security feature that limits the damage from token theft. Users must understand when and why they need to log in again.

**Independent Test**: Can be tested by creating a token with a short expiry, waiting for expiration, and verifying rejection.

**Acceptance Scenarios**:

1. **Given** a user with an expired JWT token, **When** they attempt to access a protected endpoint, **Then** they receive a 401 Unauthorized with message indicating token expiration
2. **Given** a user receives a 401 for expired token, **When** they log in again, **Then** they receive a fresh token with a new 7-day expiry
3. **Given** a token that will expire in 1 hour, **When** the user makes a request, **Then** the request succeeds (token is valid until exact expiration)

---

### User Story 5 - Invalid Token Handling (Priority: P2)

A request contains a malformed, tampered, or otherwise invalid JWT token. The system detects this and rejects the request without exposing internal details.

**Why this priority**: Protection against token tampering and injection attacks is essential for security. Invalid tokens should fail fast and safely.

**Independent Test**: Can be tested by sending requests with various malformed tokens and verifying consistent rejection.

**Acceptance Scenarios**:

1. **Given** a request with a malformed JWT (not valid base64), **When** sent to a protected endpoint, **Then** it receives 401 with generic "invalid token" message
2. **Given** a request with a JWT signed by a different secret, **When** sent to a protected endpoint, **Then** it receives 401 with generic "invalid token" message
3. **Given** a request with a JWT with tampered payload, **When** sent to a protected endpoint, **Then** it receives 401 with generic "invalid token" message
4. **Given** any invalid token scenario, **When** the error is returned, **Then** no internal details (secret, algorithm, etc.) are exposed

---

### User Story 6 - User Logout (Priority: P2)

A user wants to end their session. They trigger logout which clears their authentication state from the client.

**Why this priority**: Logout completes the authentication lifecycle and is important for shared devices and security-conscious users.

**Independent Test**: Can be tested by logging in, logging out, and verifying the token is no longer accepted on the client side.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they trigger logout, **Then** their local authentication state is cleared
2. **Given** a logged out user, **When** they attempt to access protected resources, **Then** they are redirected to login
3. **Given** a user logs out, **When** they check local storage/cookies, **Then** no authentication tokens remain

---

### User Story 7 - JWT User ID Mismatch Protection (Priority: P1)

A malicious user attempts to access another user's resources by modifying the URL to contain a different user_id while using their own valid JWT. The system detects this mismatch and blocks access.

**Why this priority**: This is the critical data isolation enforcement. Without this, authenticated users could access other users' data by URL manipulation.

**Independent Test**: Can be tested by authenticating as User A, then attempting to access User B's tasks via URL manipulation, verifying 403 response.

**Acceptance Scenarios**:

1. **Given** User A is authenticated, **When** they request `/api/v1/{user_B_id}/tasks`, **Then** they receive 403 Forbidden
2. **Given** User A is authenticated, **When** they request `/api/v1/{user_A_id}/tasks`, **Then** they receive their tasks normally
3. **Given** a 403 Forbidden response for user_id mismatch, **When** the error is examined, **Then** it does not reveal the existence of the other user

---

### Edge Cases

- What happens when a user tries to signup with SQL injection in email? → Input sanitized, treated as invalid email format
- What happens when JWT contains valid signature but user_id that doesn't exist in database? → 401 Unauthorized (user not found)
- What happens when two users try to signup with same email simultaneously? → Database unique constraint prevents duplicate, one receives error
- What happens when BETTER_AUTH_SECRET is changed while tokens are in circulation? → All existing tokens become invalid, users must re-login
- What happens when request has both invalid token AND user_id mismatch? → 401 returned first (authentication before authorization)
- What happens when Authorization header is present but empty? → 401 Unauthorized
- What happens when token is valid but user account has been deleted? → 401 Unauthorized (user not found)

## Requirements *(mandatory)*

### Functional Requirements

**Authentication Setup (R1-R2)**

- **R-001**: System MUST integrate Better Auth on the frontend (Next.js) with JWT plugin configured for 7-day token expiry
- **R-002**: System MUST share BETTER_AUTH_SECRET between frontend and backend via environment variables (minimum 32 characters)

**User Registration (R3)**

- **R-003**: System MUST allow users to create accounts with email (unique, valid format) and password (minimum 8 characters)
- **R-004**: System MUST hash all passwords using bcrypt before storage (never store plaintext)
- **R-005**: System MUST return validation errors for invalid signup data without revealing whether email exists (for security)

**User Authentication (R4)**

- **R-006**: System MUST authenticate users via email/password and issue JWT tokens upon successful login
- **R-007**: System MUST return generic "invalid credentials" error for both wrong password and non-existent email
- **R-008**: System MUST include user_id and expiration timestamp in JWT payload

**JWT Verification Middleware (R5-R6)**

- **R-009**: System MUST implement FastAPI middleware that extracts and validates JWT from Authorization header
- **R-010**: System MUST verify JWT signature using BETTER_AUTH_SECRET on every protected request
- **R-011**: System MUST reject expired tokens with 401 Unauthorized status

**Protected Routes (R7)**

- **R-012**: System MUST protect all 6 task endpoints: GET/POST /{user_id}/tasks, GET/PUT/DELETE /{user_id}/tasks/{id}, PATCH /{user_id}/tasks/{id}/complete
- **R-013**: System MUST require valid JWT for all protected endpoints (401 if missing or invalid)

**User ID Verification (R8)**

- **R-014**: System MUST verify that JWT user_id matches URL path user_id on every protected request
- **R-015**: System MUST return 403 Forbidden when user_id mismatch is detected
- **R-016**: System MUST NOT reveal whether the target user exists in 403 responses

**Error Handling (R9)**

- **R-017**: System MUST return consistent error format: `{"detail": "message", "status_code": XXX}`
- **R-018**: System MUST return 401 for authentication failures (missing, invalid, expired token)
- **R-019**: System MUST return 403 for authorization failures (user_id mismatch)
- **R-020**: System MUST NOT expose internal error details, stack traces, or secret information

**Frontend Integration (R10)**

- **R-021**: Frontend MUST store JWT token securely after login (httpOnly cookie preferred, or secure localStorage)
- **R-022**: Frontend MUST include JWT in Authorization header for all API requests: `Bearer {token}`
- **R-023**: Frontend MUST handle 401 responses by redirecting to login page
- **R-024**: Frontend MUST clear authentication state on logout

### Key Entities

- **User**: Represents a registered user with unique identifier (UUID), email (unique), password_hash (bcrypt), optional display name, and timestamps. Users own zero or more tasks and are the subject of JWT tokens.

- **JWT Token**: Represents an authentication credential containing user_id (UUID), issued_at timestamp, and expiration timestamp (7 days from issue). Tokens are signed with BETTER_AUTH_SECRET and transmitted in Authorization headers.

- **Session** (conceptual): The authenticated state maintained client-side via JWT. Not stored server-side (stateless architecture). Ends on logout or token expiration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Authentication Flow**

- **SC-001**: Users can complete signup in under 30 seconds with clear validation feedback
- **SC-002**: Users can complete login in under 10 seconds and immediately access their tasks
- **SC-003**: 100% of signup attempts with valid data succeed on first try
- **SC-004**: 100% of login attempts with valid credentials succeed on first try

**Security Verification**

- **SC-005**: 100% of requests without valid JWT to protected endpoints return 401
- **SC-006**: 100% of requests with user_id mismatch return 403
- **SC-007**: 0% of error responses expose internal details (secrets, stack traces)
- **SC-008**: Password verification adds less than 100ms to login time

**Token Management**

- **SC-009**: Tokens remain valid for exactly 7 days (±1 minute tolerance)
- **SC-010**: Expired tokens are rejected within 1 second with clear error
- **SC-011**: JWT verification middleware adds less than 50ms latency per request

**Data Isolation**

- **SC-012**: Cross-user testing confirms 100% isolation (User A cannot access User B's data)
- **SC-013**: URL manipulation attacks are blocked 100% of the time with 403

**Frontend Integration**

- **SC-014**: Frontend correctly handles all authentication states (logged in, logged out, expired)
- **SC-015**: Logout clears all authentication state within 1 second

## Assumptions

- Better Auth handles JWT generation and signing; backend only verifies signatures
- BETTER_AUTH_SECRET will be a secure random string of at least 32 characters
- Frontend and backend will use the same secret (configured via environment variables)
- User table already exists from Spec 1 (Backend Foundation)
- Health endpoint (/health) remains public (no authentication required)
- Password requirements: minimum 8 characters (additional complexity rules deferred)
- Email verification is out of scope for this spec (can be added later)
- Refresh tokens are out of scope; users re-login after token expiry
- Rate limiting for login attempts is out of scope for this spec

## Out of Scope

- Email verification / confirmation flow
- Password reset / forgot password
- Refresh token mechanism
- OAuth / social login providers
- Multi-factor authentication (MFA)
- Session management UI (active sessions list)
- Account deletion
- Password complexity requirements beyond minimum length
- Login attempt rate limiting / account lockout
- Remember me functionality
- JWT token revocation / blacklisting
