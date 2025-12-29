import uuid
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class RegisterAPI(APIView):
    def post(self, request):
        logger.info("Register attempt for username=%s", request.data.get("username"))

        User.objects.create_user(
            username=request.data["username"],
            password=request.data["password"]
        )

        logger.info("User registered successfully")
        return Response({"message": "Registered"}, status=201)

class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        logger.info("Login attempt for username=%s", username)

        user = authenticate(
            username=username,
            password=request.data.get("password")
        )

        if not user:
            logger.warning("Login failed for username=%s", username)
            return Response({"error": "Invalid"}, status=401)

        login(request, user)
        logger.info("Login successful for user_id=%s", user.id)

        return Response({"message": "Logged in"})


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logger.info("Logout request by user_id=%s", request.user.id)
        logout(request)
        logger.info("Logout successful")
        return Response({"message": "Logout successful"})
    

class TaskAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("Task list requested by user_id=%s", request.user.id)

        status_filter = request.GET.get("status")
        page = int(request.GET.get("page", 1))
        limit = 3
        offset = (page - 1) * limit

        logger.debug("Filters status=%s page=%s", status_filter, page)

        query = """
            SELECT id, title, description, due_date, status
            FROM tasks_task
            WHERE created_by = %s
        """
        params = [request.user.id]

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor = connection.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()

        tasks = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "due_date": row[3],
                "status": row[4],
            }
            for row in rows
        ]

        logger.info("Returned %s tasks for user_id=%s", len(tasks), request.user.id)
        return Response(tasks, status=200)

    def post(self, request):
        logger.info("Create task request by user_id=%s", request.user.id)

        try:
            data = request.data
            logger.debug("Task payload=%s", data)

            task_id = str(uuid.uuid4())
            logger.info("Generated task_id=%s", task_id)

            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO tasks_task
                (id, title, description, due_date, status, created_by, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, datetime('now'), datetime('now'))
                """,
                [
                    task_id,
                    data.get("title"),
                    data.get("description"),
                    data.get("due_date"),
                    data.get("status", "Pending"),
                    request.user.id
                ]
            )

            logger.info("Task created successfully task_id=%s", task_id)

            return Response(
                {"message": "Task created", "id": task_id},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.exception("Task creation failed")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        logger.info("Fetch task_id=%s by user_id=%s", task_id, request.user.id)

        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, title, description, due_date, status "
            "FROM tasks_task WHERE id=%s AND created_by=%s",
            [task_id, request.user.id]
        )
        row = cursor.fetchone()

        if not row:
            logger.warning("Task not found task_id=%s", task_id)
            return Response({"error": "Task not found"}, status=404)

        task = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "due_date": row[3],
            "status": row[4],
        }

        logger.info("Task fetched successfully task_id=%s", task_id)
        return Response(task, status=200)

    def put(self, request, task_id):
        logger.info("Update task_id=%s by user_id=%s", task_id, request.user.id)

        cursor = connection.cursor()
        cursor.execute(
            "SELECT title, description, due_date, status "
            "FROM tasks_task WHERE id=%s AND created_by=%s",
            [task_id, request.user.id]
        )
        row = cursor.fetchone()

        if not row:
            logger.warning("Task not found for update task_id=%s", task_id)
            return Response({"error": "Task not found"}, status=404)

        data = request.data

        cursor.execute(
            """
            UPDATE tasks_task SET
            title=%s,
            description=%s,
            due_date=%s,
            status=%s,
            updated_at=datetime('now')
            WHERE id=%s AND created_by=%s
            """,
            [
                data.get("title", row[0]),
                data.get("description", row[1]),
                data.get("due_date", row[2]),
                data.get("status", row[3]),
                task_id,
                request.user.id
            ]
        )

        logger.info("Task updated task_id=%s", task_id)
        return Response({"message": "Task updated"}, status=200)

    def patch(self, request, task_id):
        logger.info("Patch status for task_id=%s", task_id)

        status_value = request.data.get("status")
        if not status_value:
            logger.warning("Missing status in PATCH task_id=%s", task_id)
            return Response({"error": "Status is required"}, status=400)

        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE tasks_task
            SET status=%s, updated_at=datetime('now')
            WHERE id=%s AND created_by=%s
            """,
            [status_value, task_id, request.user.id]
        )

        if cursor.rowcount == 0:
            logger.warning("Task not found in PATCH task_id=%s", task_id)
            return Response({"error": "Task not found"}, status=404)

        logger.info("Task status updated task_id=%s", task_id)
        return Response({"message": "Status updated"}, status=200)

    def delete(self, request, task_id):
        logger.info("Delete task_id=%s by user_id=%s", task_id, request.user.id)

        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM tasks_task WHERE id=%s AND created_by=%s",
            [task_id, request.user.id]
        )

        logger.info("Task deleted task_id=%s", task_id)
        return Response({"message": "Task deleted"}, status=200)
