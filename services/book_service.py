"""
Book Service - Manage library inventory
"""

from database import execute_query
from utils.validators import is_empty, is_positive_integer, sanitize_string
from services.auth_service import log_action


def get_all_books(search: str = None):
    """Return all books, optionally filtered by search term."""
    if search and not is_empty(search):
        term = f"%{search.strip()}%"
        return execute_query(
            """
            SELECT * FROM books
            WHERE Title LIKE %s OR Author LIKE %s OR ISBN LIKE %s OR Category LIKE %s
            ORDER BY Title
            """,
            (term, term, term, term),
            fetchall=True
        )
    return execute_query("SELECT * FROM books ORDER BY Title", fetchall=True)


def get_book_by_id(book_id: int):
    return execute_query(
        "SELECT * FROM books WHERE BookID = %s",
        (book_id,),
        fetchone=True
    )


def add_book(isbn, title, author, category, quantity, user_id=None):
    title = sanitize_string(title)
    author = sanitize_string(author)
    category = sanitize_string(category)
    isbn = sanitize_string(isbn) if isbn else None

    if is_empty(title) or is_empty(author):
        return False, "Title and Author are required."

    if not is_positive_integer(quantity):
        return False, "Quantity must be a positive number."

    quantity = int(quantity)

    try:
        # Check duplicate ISBN
        if isbn:
            existing = execute_query(
                "SELECT BookID FROM books WHERE ISBN = %s", (isbn,), fetchone=True
            )
            if existing:
                return False, "A book with this ISBN already exists."

        book_id = execute_query(
            """
            INSERT INTO books (ISBN, Title, Author, Category, Quantity, AvailableQuantity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (isbn, title, author, category, quantity, quantity),
            commit=True
        )
        if user_id:
            log_action(user_id, f"Book added: {title} (ID: {book_id})")
        return True, book_id
    except Exception as e:
        return False, str(e)


def update_book(book_id, isbn, title, author, category, quantity, user_id=None):
    title = sanitize_string(title)
    author = sanitize_string(author)
    category = sanitize_string(category)
    isbn = sanitize_string(isbn) if isbn else None

    if is_empty(title) or is_empty(author):
        return False, "Title and Author are required."

    if not is_positive_integer(quantity):
        return False, "Quantity must be a positive number."

    quantity = int(quantity)

    try:
        current = get_book_by_id(book_id)
        if not current:
            return False, "Book not found."

        # Adjust available quantity proportionally if total quantity changes
        issued = current["Quantity"] - current["AvailableQuantity"]
        new_available = max(0, quantity - issued)

        execute_query(
            """
            UPDATE books
            SET ISBN=%s, Title=%s, Author=%s, Category=%s, Quantity=%s, AvailableQuantity=%s
            WHERE BookID=%s
            """,
            (isbn, title, author, category, quantity, new_available, book_id),
            commit=True
        )
        if user_id:
            log_action(user_id, f"Book updated: {title} (ID: {book_id})")
        return True, "Book updated successfully."
    except Exception as e:
        return False, str(e)


def delete_book(book_id, user_id=None):
    try:
        book = get_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        # Check if book is currently issued
        active = execute_query(
            "SELECT IssueID FROM issues WHERE BookID = %s AND Status = 'Issued'",
            (book_id,),
            fetchone=True
        )
        if active:
            return False, "Cannot delete. This book is currently issued."

        execute_query("DELETE FROM books WHERE BookID = %s", (book_id,), commit=True)
        if user_id:
            log_action(user_id, f"Book deleted: {book['Title']} (ID: {book_id})")
        return True, "Book deleted successfully."
    except Exception as e:
        return False, str(e)


def get_book_stats():
    """Return basic book statistics."""
    total = execute_query("SELECT COUNT(*) as cnt FROM books", fetchone=True)
    available = execute_query(
        "SELECT COALESCE(SUM(AvailableQuantity), 0) as cnt FROM books", fetchone=True
    )
    total_qty = execute_query(
        "SELECT COALESCE(SUM(Quantity), 0) as cnt FROM books", fetchone=True
    )
    return {
        "total_titles": total["cnt"] if total else 0,
        "total_copies": total_qty["cnt"] if total_qty else 0,
        "available_copies": available["cnt"] if available else 0
    }
