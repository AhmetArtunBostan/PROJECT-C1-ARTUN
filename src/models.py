from datetime import datetime
from enum import StrEnum
from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel, constr, ConfigDict
from typing import Optional

from .database import Base

class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default=TaskStatus.TODO.value)
    priority = Column(String, default=Priority.MEDIUM.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models
class TaskBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    description: constr(max_length=500)
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[constr(max_length=500)] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None

class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
