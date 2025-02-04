import pytest
from fastapi import status
from src.models import TaskStatus, Priority

def test_create_task(client):
    """Test creating a new task."""
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_read_tasks(client):
    """Test reading all tasks."""
    # First create a task
    client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Task"

def test_read_task(client):
    """Test reading a specific task."""
    # First create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_update_task(client):
    """Test updating a task."""
    # First create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]
    
    # Update the task
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "status": "in_progress",
            "priority": "high"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"

def test_delete_task(client):
    """Test deleting a task."""
    # First create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify task is deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_create_task_invalid_data(client):
    """Test creating a task with invalid data."""
    response = client.post(
        "/tasks/",
        json={
            "title": "",  # Empty title should be invalid
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_task_not_found(client):
    """Test updating a non-existent task."""
    response = client.put(
        "/tasks/999",
        json={
            "status": "in_progress",
            "priority": "high"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_task_not_found(client):
    """Test deleting a non-existent task."""
    response = client.delete("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
