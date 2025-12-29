# Authentication APIs
1️ Register User

POST /api/auth/register/

Description:
Create a new user account.

Request Body (JSON):

{
  "username": "john_doe",
  "password": "secret123"
}


Responses:

Status	Description
201	User registered successfully
400	Invalid request

---------------------------------------------------------------------------------

2️ Login

POST /api/auth/login/

Description:
Authenticate user and create session.

Request Body:

{
  "username": "john_doe",
  "password": "secret123"
}


Responses:

Status	Description
200	Login successful
401	Invalid credentials

Uses session-based authentication (Django login).

---------------------------------------------------------------------------------

3️ Logout

POST /api/auth/logout/
Authentication required

Responses:

Status	Description
200	Logout successful
401	Unauthorized
 
---------------------------------------------------------------------------------

# Task APIs

1 List Tasks

GET /api/tasks/
Auth required

Query Parameters:

Param	Type	Description
status	string	Filter by status (Pending, In Progress, Completed)
page	int	Page number (default = 1)

Response:

[
  {
    "id": "uuid",
    "title": "My Task",
    "description": "Details",
    "due_date": "2025-01-01",
    "status": "Pending"
  }
]

---------------------------------------------------------------------------------

2 Create Task

POST /api/tasks/
 Auth required

Request Body:

{
  "title": "New Task",
  "description": "Some details",
  "due_date": "2025-01-01",
  "status": "Pending"
}


Responses:

Status	Description
201	Task created
401	Unauthorized
500	Server error

---------------------------------------------------------------------------------

3 Get Task Detail

GET /api/tasks/{task_id}/

Auth required

Response:

{
  "id": "uuid",
  "title": "Task title",
  "description": "Task desc",
  "due_date": "2025-01-01",
  "status": "Pending"
}


Errors:

Status	Reason
404	Task not found

---------------------------------------------------------------------------------

4 Update Task (Full Update)

PUT /api/tasks/{task_id}/
Auth required

Request Body:

{
  "title": "Updated title",
  "description": "Updated desc",
  "due_date": "2025-02-01",
  "status": "Completed"
}


Response:

{ "message": "Task updated" }

---------------------------------------------------------------------------------

5 Update Task Status (Partial Update)

PATCH /api/tasks/{task_id}/

Auth required

Request Body:

{
  "status": "Completed"
}


Responses:

Status	Description
200	Status updated
400	Status missing
404	Task not found

---------------------------------------------------------------------------------

6 Delete Task

DELETE /api/tasks/{task_id}/
 Auth required

Response:

{ "message": "Task deleted" }


# Authorization Notes

Authentication: Django Session
Each task is user-scoped
Users can only access their own tasks

--> Design Decisions

No ORM used (raw SQL via connection.cursor)
UUID used as primary key
Pagination implemented manually
Logging added for all operations
Exception handling included

# Testing

APIs tested using pytest + DRF APIClient

Tests include:
Auth flows
CRUD operations
Authorization checks