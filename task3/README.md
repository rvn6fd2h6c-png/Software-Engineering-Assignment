Task 3: Authentication and Authorization in Flask API
University Information
University: SZABIST University Larkana
Department: Computer Science
Course: CSC3109 Software Engineering
Assignment: Assignment 1
Instructor: Abdul Muqtadar
Project Description

This project is an Employee Management API developed using Python Flask and SQLite.

It implements user authentication using JWT tokens and role-based authorization.

Technologies Used
Python
Flask
SQLite
PyJWT
PowerShell and cURL
User Roles
1. Employee
Can view employee records.
Cannot add, update, or delete employee records.
2. Administrator
Can view employee records.
Can add employee records.
Can update employee records.
Can delete employee records.
API Endpoints
Method	Endpoint	Description
POST	/login	User login
GET	/employees	View all employees
GET	/employees/id	View a specific employee
POST	/employees	Add employee (Admin only)
PUT	/employees/id	Update employee (Admin only)
DELETE	/employees/id	Delete employee (Admin only)
Authentication

Users must log in with valid credentials to receive a JWT token.

The token must be included in the Authorization header:

Authorization: Bearer YOUR_TOKEN

Database

SQLite is used to store employee records and user information.

Testing

The API was tested using PowerShell and cURL.

Tests performed:

Administrator login successful.
Employee login successful.
Employee can view records (200 OK).
Employee cannot add records (403 Forbidden).
Administrator can add records.
Administrator can update records.
Administrator can delete records.
Unauthenticated requests are rejected (401 Unauthorized).
Invalid login credentials are rejected.
How to Run the Project
Install Python.
Install dependencies:

pip install -r requirements.txt

Run the Flask application:

python app.py

API address:

http://127.0.0.1:5001

Project Files
app.py: Flask API and authentication/authorization logic.
database.py: SQLite database creation.
employees.db: SQLite database.
requirements.txt: Required Python packages.
screenshots/: API testing screenshots.
video/: Video demonstration.
Conclusion

The project demonstrates how authentication and role-based authorization can secure a Flask API and restrict access according to user roles.