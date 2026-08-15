"""
Transaction Service - Issue and Return books
"""

from database import execute_query
from utils.date_utils import today_str, calculate_due_date
from services.fine_service import calculate_fine
from services.auth_service import log_action
from services.book_service import get_book_by_id
from services.student_service import get_student_by_id
from config import DEFAULT_LOAN_DAYS, DEFAULT_FINE_RATE, MAX_BOOKS_PER_STUDENT


def count_active_issues_for_student(student_id: int) -> int:
    """How many books this student currently has (not returned)."""
    row = execute_query(
        "SELECT COUNT(*) as cnt FROM issues WHERE StudentID = %s AND Status = 'Issued'",
        (student_id,),
        fetchone=True
    )
    return int(row["cnt"]) if row else 0


def issue_book(student_id, book_id, user_id=None, loan_days=None):
    """
    Issue a book to a student.
    Rules:
    - Student and book must exist
    - Book must have available copies
    - Student may not have more than MAX_BOOKS_PER_STUDENT active issues
    Returns (success: bool, message: str)
    """
    try:
        student_id = int(student_id)
        book_id = int(book_id)
    except (TypeError, ValueError):
        return False, "Invalid Student ID or Book ID."

    student = get_student_by_id(student_id)
    if not student:
        return False, "Student not found."

    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book["AvailableQuantity"] <= 0:
        return False, "No copies available for this book."

    # Max 6 books rule
    active_count = count_active_issues_for_student(student_id)
    if active_count >= MAX_BOOKS_PER_STUDENT:
        return False, (
            f"Student already has {active_count} books issued. "
            f"Maximum allowed is {MAX_BOOKS_PER_STUDENT}. "
            f"Please return at least one book first."
        )

    issue_date = today_str()
    due_date = calculate_due_date(issue_date, loan_days or DEFAULT_LOAN_DAYS)

    try:
        issue_id = execute_query(
            """
            INSERT INTO issues (BookID, StudentID, IssueDate, DueDate, Status)
            VALUES (%s, %s, %s, %s, 'Issued')
            """,
            (book_id, student_id, issue_date, due_date),
            commit=True
        )

        execute_query(
            "UPDATE books SET AvailableQuantity = AvailableQuantity - 1 WHERE BookID = %s",
            (book_id,),
            commit=True
        )

        if user_id:
            log_action(
                user_id,
                f"Book issued: BookID {book_id} to StudentID {student_id} (IssueID: {issue_id})"
            )

        remaining = MAX_BOOKS_PER_STUDENT - (active_count + 1)
        return True, (
            f"Book issued successfully.\n"
            f"Due date: {due_date} (1 month loan)\n"
            f"Student can still borrow {remaining} more book(s)."
        )
    except Exception as e:
        return False, str(e)


def get_active_issues(search: str = None):
    """Return currently issued books (Status = 'Issued')."""
    query = """
        SELECT i.IssueID, i.BookID, i.StudentID, i.IssueDate, i.DueDate, i.Status,
               b.Title, b.Author, s.Name as StudentName
        FROM issues i
        JOIN books b ON i.BookID = b.BookID
        JOIN students s ON i.StudentID = s.StudentID
        WHERE i.Status = 'Issued'
    """
    if search:
        term = f"%{search.strip()}%"
        query += " AND (b.Title LIKE %s OR s.Name LIKE %s OR CAST(i.IssueID AS CHAR) LIKE %s)"
        return execute_query(query + " ORDER BY i.DueDate", (term, term, term), fetchall=True)
    return execute_query(query + " ORDER BY i.DueDate", fetchall=True)


def get_issue_by_id(issue_id: int):
    return execute_query(
        """
        SELECT i.*, b.Title, b.Author, s.Name as StudentName
        FROM issues i
        JOIN books b ON i.BookID = b.BookID
        JOIN students s ON i.StudentID = s.StudentID
        WHERE i.IssueID = %s
        """,
        (issue_id,),
        fetchone=True
    )


def return_book(issue_id, user_id=None, fine_rate=None):
    """
    Return a book, calculate fine, update inventory.
    Returns (success: bool, message: str, fine: float)
    """
    try:
        issue_id = int(issue_id)
    except (TypeError, ValueError):
        return False, "Invalid Issue ID.", 0.0

    issue = get_issue_by_id(issue_id)
    if not issue:
        return False, "Transaction not found.", 0.0

    if issue["Status"] == "Returned":
        return False, "This book has already been returned.", 0.0

    return_date = today_str()
    fine = calculate_fine(issue["DueDate"], return_date, fine_rate or DEFAULT_FINE_RATE)

    try:
        execute_query(
            """
            UPDATE issues
            SET ReturnDate = %s, Fine = %s, Status = 'Returned'
            WHERE IssueID = %s
            """,
            (return_date, fine, issue_id),
            commit=True
        )

        execute_query(
            "UPDATE books SET AvailableQuantity = AvailableQuantity + 1 WHERE BookID = %s",
            (issue["BookID"],),
            commit=True
        )

        if user_id:
            log_action(
                user_id,
                f"Book returned: IssueID {issue_id}, Fine: Rs.{fine}"
            )

        msg = f"Book returned successfully. Fine: Rs.{fine:.2f}"
        return True, msg, fine
    except Exception as e:
        return False, str(e), 0.0


def get_transaction_stats():
    issued = execute_query(
        "SELECT COUNT(*) as cnt FROM issues WHERE Status = 'Issued'", fetchone=True
    )
    overdue = execute_query(
        """
        SELECT COUNT(*) as cnt FROM issues
        WHERE Status = 'Issued' AND DueDate < CURDATE()
        """,
        fetchone=True
    )
    total_fines = execute_query(
        "SELECT COALESCE(SUM(Fine), 0) as total FROM issues WHERE Status = 'Returned'",
        fetchone=True
    )
    return {
        "issued_books": issued["cnt"] if issued else 0,
        "overdue_books": overdue["cnt"] if overdue else 0,
        "total_fines": float(total_fines["total"]) if total_fines else 0.0
    }
