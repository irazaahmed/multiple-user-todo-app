# Quickstart: Backend Foundation

**Feature**: 001-backend-foundation
**Date**: 2026-02-04

## Prerequisites

- Python 3.13+ installed
- Neon PostgreSQL account with database created
- Git repository cloned

## Setup Steps

### 1. Create Backend Directory

```bash
cd Full-Stack-Multi-User-Todo
mkdir -p backend/routes
touch backend/__init__.py
touch backend/routes/__init__.py
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlmodel==0.0.22
psycopg2-binary==2.9.10
python-dotenv==1.0.1
pydantic==2.10.0
```

### 4. Configure Environment Variables

Create `.env` file in backend directory:

```bash
# Get connection string from Neon dashboard
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Frontend URL for CORS
CORS_ORIGINS=http://localhost:3000
```

### 5. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "database": "connected"}
```

## Testing Endpoints

### Create Test User (SQL)

Run in Neon SQL Editor:
```sql
INSERT INTO users (id, email, password_hash, name)
VALUES (
  '123e4567-e89b-12d3-a456-426614174000',
  'test@example.com',
  '$2b$12$dummy_hash_for_testing',
  'Test User'
);
```

### Test CRUD Operations

```bash
# Set user ID variable
USER_ID="123e4567-e89b-12d3-a456-426614174000"

# Create task
curl -X POST "http://localhost:8000/api/v1/${USER_ID}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# List tasks
curl "http://localhost:8000/api/v1/${USER_ID}/tasks"

# List pending tasks only
curl "http://localhost:8000/api/v1/${USER_ID}/tasks?status=pending"

# Get single task (replace 1 with actual task ID)
curl "http://localhost:8000/api/v1/${USER_ID}/tasks/1"

# Update task
curl -X PUT "http://localhost:8000/api/v1/${USER_ID}/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and fruits"}'

# Toggle completion
curl -X PATCH "http://localhost:8000/api/v1/${USER_ID}/tasks/1/complete"

# Delete task
curl -X DELETE "http://localhost:8000/api/v1/${USER_ID}/tasks/1"
```

### Test Validation Errors

```bash
# Missing title (expect 422)
curl -X POST "http://localhost:8000/api/v1/${USER_ID}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"description": "No title"}'

# Title too long (expect 422)
curl -X POST "http://localhost:8000/api/v1/${USER_ID}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "'$(printf 'a%.0s' {1..201})'"}'

# Invalid UUID (expect 400)
curl "http://localhost:8000/api/v1/invalid-uuid/tasks"
```

### Test Data Isolation

```bash
# Create second user
USER_B="223e4567-e89b-12d3-a456-426614174001"

# Try to access User A's task as User B (expect 404)
curl "http://localhost:8000/api/v1/${USER_B}/tasks/1"
```

## File Structure After Setup

```
backend/
├── __init__.py
├── main.py              # FastAPI app entry
├── models.py            # SQLModel User & Task
├── db.py                # Database connection
├── schemas.py           # Pydantic schemas
├── routes/
│   ├── __init__.py
│   └── tasks.py         # Task CRUD endpoints
├── requirements.txt
├── .env                 # Local config (gitignored)
├── .env.example         # Template for env vars
└── README.md
```

## Common Issues

### Connection Error to Neon

- Verify DATABASE_URL has `?sslmode=require` at end
- Check Neon dashboard for correct connection string
- Ensure database exists and is not suspended

### Module Not Found

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### CORS Errors in Browser

- Verify CORS_ORIGINS matches your frontend URL exactly
- Include protocol (http:// or https://)
- No trailing slash

### Tables Not Created

- Check database connection in health endpoint first
- Verify user has CREATE TABLE permissions in Neon

## Next Steps

After backend is working:
1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to build the code
3. Test all endpoints with Postman
4. Proceed to Spec 2 (Authentication with Better Auth)
