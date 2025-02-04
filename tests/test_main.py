import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.main import app, get_db
from src.models import Task, TaskStatus, Priority

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"

def test_read_tasks():
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_task():
    # First create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]

    # Then read it
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_update_task():
    # First create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]

    # Then update it
    response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "status": "in_progress"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "in_progress"

def test_delete_task():
    # First create a task
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404

def test_invalid_task_status():
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "invalid_status",
            "priority": "medium"
        }
    )
    assert response.status_code == 422

def test_invalid_task_priority():
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "invalid_priority"
        }
    )
    assert response.status_code == 422
