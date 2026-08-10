"""
Student Service - Manage student records
"""

from database import execute_query
from utils.validators import is_empty, sanitize_string, is_valid_phone
from services.auth_service import log_action


def get_all_students(search: str = None):
    if search and not is_empty(search):
        term = f"%{search.strip()}%"
        return execute_query(
            """
            SELECT * FROM students
            WHERE Name LIKE %s OR Department LIKE %s OR Phone LIKE %s OR StudentID LIKE %s
            ORDER BY Name
            """,
            (term, term, term, term),
            fetchall=True
        )
    return execute_query("SELECT * FROM students ORDER BY Name", fetchall=True)


def get_student_by_id(student_id: int):
    return execute_query(
        "SELECT * FROM students WHERE StudentID = %s",
        (student_id,),
        fetchone=True
    )


def add_student(name, department, semester, phone, user_id=None):
    name = sanitize_string(name)
    department = sanitize_string(department)
    semester = sanitize_string(semester)
    phone = sanitize_string(phone)

    if is_empty(name):
        return False, "Student name is required."

    if phone and not is_valid_phone(phone):
        return False, "Invalid phone number."

    try:
        student_id = execute_query(
            """
            INSERT INTO students (Name, Department, Semester, Phone)
            VALUES (%s, %s, %s, %s)
            """,
            (name, department, semester, phone),
            commit=True
        )
        if user_id:
            log_action(user_id, f"Student added: {name} (ID: {student_id})")
        return True, student_id
    except Exception as e:
        return False, str(e)


def update_student(student_id, name, department, semester, phone, user_id=None):
    name = sanitize_string(name)
    department = sanitize_string(department)
    semester = sanitize_string(semester)
    phone = sanitize_string(phone)

    if is_empty(name):
        return False, "Student name is required."

    try:
        existing = get_student_by_id(student_id)
        if not existing:
            return False, "Student not found."

        execute_query(
            """
            UPDATE students
            SET Name=%s, Department=%s, Semester=%s, Phone=%s
            WHERE StudentID=%s
            """,
            (name, department, semester, phone, student_id),
            commit=True
        )
        if user_id:
            log_action(user_id, f"Student updated: {name} (ID: {student_id})")
        return True, "Student updated successfully."
    except Exception as e:
        return False, str(e)


def delete_student(student_id, user_id=None):
    try:
        student = get_student_by_id(student_id)
        if not student:
            return False, "Student not found."

        active = execute_query(
            "SELECT IssueID FROM issues WHERE StudentID = %s AND Status = 'Issued'",
            (student_id,),
            fetchone=True
        )
        if active:
            return False, "Cannot delete. Student has active issued books."

        execute_query("DELETE FROM students WHERE StudentID = %s", (student_id,), commit=True)
        if user_id:
            log_action(user_id, f"Student deleted: {student['Name']} (ID: {student_id})")
        return True, "Student deleted successfully."
    except Exception as e:
        return False, str(e)


def get_student_stats():
    total = execute_query("SELECT COUNT(*) as cnt FROM students", fetchone=True)
    return {"total_students": total["cnt"] if total else 0}
