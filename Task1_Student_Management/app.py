from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create students table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# GET all students
@app.route('/students', methods=['GET'])
def get_students():

    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# GET one student
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# POST - Add student
@app.route('/students', methods=['POST'])
def add_student():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    name = data.get('name')
    department = data.get('department')
    email = data.get('email')

    if not all([name, department, email]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()

    conn.execute(
        "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
        (name, department, email)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201


# PUT - Update student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    name = data.get('name')
    department = data.get('department')
    email = data.get('email')

    if not all([name, department, email]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()

    cursor = conn.execute(
        """UPDATE students
        SET name = ?, department = ?, email = ?
        WHERE id = ?""",
        (name, department, email, id)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated successfully"})


# DELETE student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):

    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


# Start Flask application
if __name__ == '__main__':

    create_table()

    app.run(debug=True)