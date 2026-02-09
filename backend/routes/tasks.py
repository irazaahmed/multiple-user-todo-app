from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from models import Task, User
from schemas import TaskCreate, TaskUpdate, TaskResponse
from db import get_session


# Create API router for task endpoints
router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
def get_tasks(
    user_id: UUID,
    status: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Get all tasks for a specific user.

    Args:
        user_id: The UUID of the user whose tasks to retrieve
        status: Optional filter for task status (pending, completed, all)
        session: Database session

    Returns:
        List of tasks for the user
    """
    # Build query to get tasks for user
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter if provided
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Order by creation date (newest first)
    query = query.order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    return tasks


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new task for a user.

    Args:
        user_id: The UUID of the user creating the task
        task_data: Task creation data (title, description)
        session: Database session

    Returns:
        Created task with 201 status
    """
    # Create new task instance
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False  # Default to not completed
    )

    # Add to session and commit
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_single_task(
    user_id: UUID,
    task_id: int,
    session: Session = Depends(get_session)
):
    """
    Get a single task by its ID.

    Args:
        user_id: The UUID of the user requesting the task
        task_id: The ID of the task to retrieve
        session: Database session

    Returns:
        The requested task

    Raises:
        HTTPException 404: If task doesn't exist or belongs to different user
    """
    # Query for task with both user_id and task_id (enforce data isolation)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: UUID,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session)
):
    """
    Update an existing task.

    Args:
        user_id: The UUID of the user updating the task
        task_id: The ID of the task to update
        task_data: Task update data (title, description)
        session: Database session

    Returns:
        Updated task

    Raises:
        HTTPException 404: If task doesn't exist or belongs to different user
    """
    # Query for existing task with both user_id and task_id (enforce data isolation)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields if provided in task_data
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    # Update the updated_at timestamp
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    # Add to session and commit
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: UUID,
    task_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a task.

    Args:
        user_id: The UUID of the user deleting the task
        task_id: The ID of the task to delete
        session: Database session

    Returns:
        204 No Content

    Raises:
        HTTPException 404: If task doesn't exist or belongs to different user
    """
    # Query for existing task with both user_id and task_id (enforce data isolation)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete the task
    session.delete(task)
    session.commit()

    # Return 204 No Content
    return


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    user_id: UUID,
    task_id: int,
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task.

    Args:
        user_id: The UUID of the user toggling the task
        task_id: The ID of the task to toggle
        session: Database session

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException 404: If task doesn't exist or belongs to different user
    """
    # Query for existing task with both user_id and task_id (enforce data isolation)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle the completion status
    task.completed = not task.completed

    # Update the updated_at timestamp
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    # Add to session and commit
    session.add(task)
    session.commit()
    session.refresh(task)

    return task