"""
Report Service
"""

from database import execute_query
from datetime import datetime
import os
from config import REPORTS_DIR


def inventory_report():
    books = execute_query(
        "SELECT BookID, ISBN, Title, Author, Category, Quantity, AvailableQuantity FROM books ORDER BY Title",
        fetchall=True
    )
    stats = execute_query(
        """
        SELECT
            COUNT(*) as total_titles,
            COALESCE(SUM(Quantity), 0) as total_copies,
            COALESCE(SUM(AvailableQuantity), 0) as available_copies,
            COALESCE(SUM(Quantity - AvailableQuantity), 0) as issued_copies
        FROM books
        """,
        fetchone=True
    )
    return {"books": books or [], "stats": stats or {}}


def overdue_report():
    rows = execute_query(
        """
        SELECT i.IssueID, b.Title, s.Name as StudentName, i.IssueDate, i.DueDate,
               DATEDIFF(CURDATE(), i.DueDate) as OverdueDays
        FROM issues i
        JOIN books b ON i.BookID = b.BookID
        JOIN students s ON i.StudentID = s.StudentID
        WHERE i.Status = 'Issued' AND i.DueDate < CURDATE()
        ORDER BY i.DueDate
        """,
        fetchall=True
    )
    return rows or []


def transaction_report(limit=100):
    rows = execute_query(
        """
        SELECT i.IssueID, b.Title, s.Name as StudentName,
               i.IssueDate, i.DueDate, i.ReturnDate, i.Fine, i.Status
        FROM issues i
        JOIN books b ON i.BookID = b.BookID
        JOIN students s ON i.StudentID = s.StudentID
        ORDER BY i.IssueID DESC
        LIMIT %s
        """,
        (limit,),
        fetchall=True
    )
    return rows or []


def student_activity_report(student_id=None):
    if student_id:
        return execute_query(
            """
            SELECT i.IssueID, b.Title, i.IssueDate, i.DueDate, i.ReturnDate, i.Fine, i.Status
            FROM issues i
            JOIN books b ON i.BookID = b.BookID
            WHERE i.StudentID = %s
            ORDER BY i.IssueDate DESC
            """,
            (student_id,),
            fetchall=True
        ) or []
    return execute_query(
        """
        SELECT s.StudentID, s.Name, COUNT(i.IssueID) as TotalIssues,
               SUM(CASE WHEN i.Status='Issued' THEN 1 ELSE 0 END) as CurrentlyIssued
        FROM students s
        LEFT JOIN issues i ON s.StudentID = i.StudentID
        GROUP BY s.StudentID, s.Name
        ORDER BY TotalIssues DESC
        """,
        fetchall=True
    ) or []


def export_report_to_text(report_name: str, content_lines: list) -> str:
    """Save a simple text report and return the file path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_name}_{timestamp}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Library Management System - {report_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for line in content_lines:
            f.write(line + "\n")

    return filepath
