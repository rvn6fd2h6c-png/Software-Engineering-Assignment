
import streamlit as st
import requests

API = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓"
)

st.title("🎓 Student Management System")

# Get all students
def get_students():
    try:
        response = requests.get(f"{API}/students")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        st.error("Flask API is not running. Please start app.py.")
        return []

# Display students
st.header("All Students")

students = get_students()

if students:
    st.dataframe(students, use_container_width=True)
else:
    st.info("No students available.")

st.divider()

# Add student
st.header("Add New Student")

with st.form("add_student_form"):
    name = st.text_input("Student Name")
    department = st.text_input("Department")
    email = st.text_input("Email")

    submit = st.form_submit_button("Add Student")

    if submit:
        if name and department and email:
            response = requests.post(
                f"{API}/students",
                json={
                    "name": name,
                    "department": department,
                    "email": email
                }
            )

            if response.status_code == 201:
                st.success("Student added successfully!")
                st.rerun()
            else:
                st.error(response.text)
        else:
            st.warning("Please fill all fields.")

st.divider()

# Update student
st.header("Update Student")

if students:
    student_ids = [s["id"] for s in students]

    selected_id = st.selectbox(
        "Select Student ID",
        student_ids
    )

    selected = next(
        s for s in students if s["id"] == selected_id
    )

    with st.form("update_student_form"):
        new_name = st.text_input(
            "Name",
            value=selected["name"]
        )

        new_department = st.text_input(
            "Department",
            value=selected["department"]
        )

        new_email = st.text_input(
            "Email",
            value=selected["email"]
        )

        update = st.form_submit_button("Update Student")

        if update:
            response = requests.put(
                f"{API}/students/{selected_id}",
                json={
                    "name": new_name,
                    "department": new_department,
                    "email": new_email
                }
            )

            if response.ok:
                st.success("Student updated successfully!")
                st.rerun()
            else:
                st.error(response.text)

st.divider()

# Delete student
st.header("Delete Student")

if students:
    delete_id = st.selectbox(
        "Select Student to Delete",
        student_ids,
        key="delete_student"
    )

    if st.button("Delete Student"):
        response = requests.delete(
            f"{API}/students/{delete_id}"
        )

        if response.ok:
            st.success("Student deleted successfully!")
            st.rerun()
        else:
            st.error(response.text)
