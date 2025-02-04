from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import os

from . import models, database
from .database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="src/templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Custom error responses
def create_error_response(status_code: int, message: str):
    return {
        "status": "error",
        "code": status_code,
        "message": message
    }

# Task validation
def validate_task(task_data: dict):
    errors = []
    
    # Title validation
    title = task_data.get("title", "").strip()
    if not title:
        errors.append("Title is required")
    elif len(title) < 3:
        errors.append("Title must be at least 3 characters long")
    elif len(title) > 100:
        errors.append("Title cannot exceed 100 characters")
    
    # Description validation
    description = task_data.get("description", "")
    if description and len(description) > 500:
        errors.append("Description cannot exceed 500 characters")
    
    # Status validation
    status = task_data.get("status")
    valid_statuses = ["todo", "in_progress", "completed"]
    if not status:
        errors.append("Status is required")
    elif status not in valid_statuses:
        errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    # Priority validation
    priority = task_data.get("priority")
    valid_priorities = ["low", "medium", "high"]
    if not priority:
        errors.append("Priority is required")
    elif priority not in valid_priorities:
        errors.append(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
    
    return errors

# Routes
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/tasks/", response_model=List[models.TaskInDB])
def read_tasks(
    status: str = None,
    priority: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Task)
    
    if status:
        try:
            status_enum = models.TaskStatus(status.lower())
            query = query.filter(models.Task.status == status_enum.value)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(400, f"Invalid status value: {status}")
            )
    
    if priority:
        try:
            priority_enum = models.Priority(priority.lower())
            query = query.filter(models.Task.priority == priority_enum.value)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(400, f"Invalid priority value: {priority}")
            )
    
    if search:
        query = query.filter(
            models.Task.title.ilike(f"%{search}%") |
            models.Task.description.ilike(f"%{search}%")
        )
    
    tasks = query.all()
    
    # Convert string values to enum objects
    for task in tasks:
        task.status = models.TaskStatus(task.status.lower())
        task.priority = models.Priority(task.priority.lower())
    
    return tasks

@app.post("/api/tasks/", response_model=models.TaskInDB)
def create_task(task: models.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority.value
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/api/tasks/{task_id}", response_model=models.TaskInDB)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(404, f"Task with id {task_id} not found")
        )
    return task

@app.put("/api/tasks/{task_id}", response_model=models.TaskInDB)
def update_task(task_id: int, task: models.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(404, f"Task with id {task_id} not found")
        )
    
    update_data = task.dict(exclude_unset=True)
    
    # Convert enum values to strings
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    if "priority" in update_data:
        update_data["priority"] = update_data["priority"].value
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(404, f"Task with id {task_id} not found")
        )
    
    try:
        db.delete(db_task)
        db.commit()
        return {"status": "success", "message": f"Task {task_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=create_error_response(500, str(e))
        )
