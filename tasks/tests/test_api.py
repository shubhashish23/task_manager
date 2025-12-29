import pytest
import uuid
from django.contrib.auth.models import User
from django.db import connection
from rest_framework.test import APIClient




@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="testpass123"
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username="testuser", password="testpass123")
    return client

@pytest.mark.django_db
def test_register_api(client):
    response = client.post(
        "/api/auth/register/",
        {
            "username": "newuser",
            "password": "newpass123"
        },
        format="json"
    )

    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_login_success(client, user):
    response = client.post(
        "/api/auth/login/",
        {
            "username": "testuser",
            "password": "testpass123"
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["message"] == "Logged in"


@pytest.mark.django_db
def test_login_failure(client):
    response = client.post(
        "/api/auth/login/",
        {
            "username": "wrong",
            "password": "wrong"
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_logout(auth_client):
    response = auth_client.post("/api/auth/logout/")
    assert response.status_code == 200
    assert response.data["message"] == "Logout successful"


@pytest.fixture(autouse=True)
def create_tasks_table(db):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks_task (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            due_date DATE,
            status TEXT,
            created_by INTEGER,
            created_at DATETIME,
            updated_at DATETIME
        )
    """)

def create_task(user_id):
    task_id = str(uuid.uuid4())

    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO tasks_task
        (id, title, description, due_date, status, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, datetime('now'), datetime('now'))
        """,
        [
            task_id,
            "Test Task",
            "Test Desc",
            "2025-01-01",
            "Pending",
            user_id
        ]
    )
    return task_id

@pytest.mark.django_db
def test_task_list(auth_client, user):
    create_task(user.id)

    response = auth_client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_task_create(auth_client):
    response = auth_client.post(
        "/api/tasks/",
        {
            "title": "New Task",
            "description": "Desc",
            "due_date": "2025-01-01",
            "status": "Pending"
        },
        format="json"
    )

    assert response.status_code == 201
    assert "id" in response.data

@pytest.mark.django_db
def test_task_detail(auth_client, user):
    task_id = create_task(user.id)

    response = auth_client.get(f"/api/tasks/{task_id}/")
    assert response.status_code == 200
    assert response.data["title"] == "Test Task"

@pytest.mark.django_db
def test_task_update(auth_client, user):
    task_id = create_task(user.id)

    response = auth_client.put(
        f"/api/tasks/{task_id}/",
        {
            "title": "Updated",
            "status": "Completed"
        },
        format="json"
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_task_patch(auth_client, user):
    task_id = create_task(user.id)

    response = auth_client.patch(
        f"/api/tasks/{task_id}/",
        {"status": "In Progress"},
        format="json"
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_task_delete(auth_client, user):
    task_id = create_task(user.id)

    response = auth_client.delete(f"/api/tasks/{task_id}/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_task_list_unauthorized(client):
    response = client.get("/api/tasks/")
    assert response.status_code in (401, 403)

