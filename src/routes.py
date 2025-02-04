from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from . import models
from .database import get_db

app = APIRouter()

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: models.TaskStatus = models.TaskStatus.TODO
    priority: models.Priority = models.Priority.MEDIUM

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[models.TaskStatus] = None
    priority: Optional[models.Priority] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks"""
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only update fields that are provided
    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_task, field):
            setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return None
