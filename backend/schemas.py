from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.
    Title is required, description is optional.
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    Both title and description are optional.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskResponse(BaseModel):
    """
    Schema for task response in API endpoints.
    Matches the Task model fields.
    """
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True