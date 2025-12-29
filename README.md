# Introduction 
Todo application built with Django and REST APIs that allows users to create, edit, delete, and track tasks. This app includes user authentication, task status tracking, and a responsive UI for managing daily tasks efficiently.

# Features

- User registration and login/logout
- Create, edit, and delete tasks
- Set task description, due date, and status (Pending, In Progress, Completed)
- Filter tasks by status
- Responsive and user-friendly interface
- Clean, modern UI with hover effects and status badges
- CSRF protected forms and secure authentication


### Tech Stack
- Django
- Django REST Framework
- SQLite
- HTML, CSS, jQuery
- Pytest django-pytest

### Setup
pip install -r requirements.txt 
python manage.py migrate  
python manage.py runserver  

### DataBase
SQLite is already in folder for sample database

### User access 
Superuser :
    username : test_super_user
    password : 1471
Normal user : 
    username : test-user
    password : asd@123

### Notes
- ORM intentionally avoided
- Raw SQL used
- APIView used instead of ViewSets