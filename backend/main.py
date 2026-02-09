from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Import models and database components
from db import init_db, get_session
import models  # noqa: F401
from routes import tasks

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup (if needed)


# Create FastAPI app with lifespan context
app = FastAPI(lifespan=lifespan)


# Configure CORS middleware reading from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "")
if cors_origins_str:
    # Split comma-separated origins
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", response_model=dict)
async def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint that verifies database connectivity.

    Returns:
        dict: Status and database connection info
    """
    try:
        # Test database connectivity with a simple query
        result = session.exec(select(1))
        _ = result.first()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # Log the error for debugging (would use proper logger in production)
        print(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"detail": "Database connection failed", "status_code": 500}
        )


# Include task router with prefix
app.include_router(tasks.router, prefix="/api/v1")


# This allows the app to be run with uvicorn
# Example: uvicorn backend.main:app --reload