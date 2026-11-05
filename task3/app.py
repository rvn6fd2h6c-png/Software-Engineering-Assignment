
import sqlite3
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = "employees.db"

# Development secret for classroom testing only.
# Set a private environment variable before deployment.
SECRET_KEY = "classroom-development-secret-change-this"


# Connect to database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create demo accounts if they don't already exist
def create_demo_users():
    conn = get_db()

    users = [
        ("admin", "admin123", "admin"),
        ("employee", "employee123", "employee")
    ]

    for username, password, role in users:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role)
            )

    conn.commit()
    conn.close()


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "")

        if not token.startswith("Bearer "):
            return jsonify({"message": "Token is missing"}), 401

        token = token.split(" ", 1)[1]

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )
            request.current_user = data

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# Administrator authorization decorator
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user["role"] != "admin":
            return jsonify({
                "message": "Access denied. Administrator only."
            }), 403

        return f(*args, **kwargs)

    return decorated


# LOGIN API
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):

        token = jwt.encode({
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token,
            "role": user["role"]
        }), 200

    return jsonify({"message": "Invalid username or password"}), 401


# GET ALL EMPLOYEES
@app.route("/employees", methods=["GET"])
@token_required
def get_employees():
    conn = get_db()

    employees = conn.execute(
        "SELECT * FROM employees"
    ).fetchall()

    conn.close()

    return jsonify([dict(emp) for emp in employees]), 200


# GET SINGLE EMPLOYEE
@app.route("/employees/<int:id>", methods=["GET"])
@token_required
def get_employee(id):
    conn = get_db()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if employee is None:
        return jsonify({"message": "Employee not found"}), 404

    return jsonify(dict(employee)), 200


# ADD EMPLOYEE - ADMIN ONLY
@app.route("/employees", methods=["POST"])
@admin_required
def add_employee():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    department = data.get("department")
    email = data.get("email")

    if not name or not department or not email:
        return jsonify({"message": "All fields are required"}), 400

    conn = get_db()

    try:
        cursor = conn.execute(
            "INSERT INTO employees (name, department, email) VALUES (?, ?, ?)",
            (name, department, email)
        )

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Employee added successfully",
            "id": new_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"}), 409

    finally:
        conn.close()


# UPDATE EMPLOYEE - ADMIN ONLY
@app.route("/employees/<int:id>", methods=["PUT"])
@admin_required
def update_employee(id):
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    department = data.get("department")
    email = data.get("email")

    if not name or not department or not email:
        return jsonify({"message": "All fields are required"}), 400

    conn = get_db()

    try:
        cursor = conn.execute(
            """UPDATE employees
               SET name = ?, department = ?, email = ?
               WHERE id = ?""",
            (name, department, email, id)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Employee not found"}), 404

        return jsonify({"message": "Employee updated successfully"}), 200

    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"}), 409

    finally:
        conn.close()


# DELETE EMPLOYEE - ADMIN ONLY
@app.route("/employees/<int:id>", methods=["DELETE"])
@admin_required
def delete_employee(id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"message": "Employee not found"}), 404

    return jsonify({"message": "Employee deleted successfully"}), 200


if __name__ == "__main__":
    create_demo_users()
    app.run(debug=True, port=5001)
