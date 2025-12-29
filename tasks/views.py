from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_view(request):
    context={
        'login': True
    }
    return render(request, "tasks/login.html" , context=context)

def register_view(request):
    context={
        'register': True
    }
    return render(request, "tasks/register.html" , context=context)

@login_required
def task_list(request):
    return render(request, "tasks/task_list.html")

@login_required
def task_add(request):
    return render(request, "tasks/task_form.html")

@login_required
def task_edit(request, task_id):
    return render(request, "tasks/task_form.html", {"task_id": task_id})

@login_required
def task_detail(request, task_id):
    return render(request, "tasks/task_detail.html", {"task_id": task_id})