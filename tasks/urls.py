from django.urls import path
from . import views, api

app_name = 'tasks'

urlpatterns = [
    # pages
    path("login/", views.login_view , name='login'),
    path("register/", views.register_view , name="register"),
    path("", views.task_list , name='task_list'),
    path("task/add/", views.task_add, name = 'task_add'),
    path("task/edit/<str:task_id>/", views.task_edit, name='task_edit' ),
    path("task/<str:task_id>/", views.task_detail , name = 'task_detail'),

    # auth APIs
    path("api/auth/register/", api.RegisterAPI.as_view()),
    path("api/auth/login/", api.LoginAPI.as_view()),
    path("api/auth/logout/", api.LogoutAPI.as_view()),

    # task APIs
    path("api/tasks/", api.TaskAPI.as_view() , name="task_list_create"),
    path("api/tasks/<str:task_id>/", api.TaskDetailAPI.as_view() , name="task_detail"),
]
