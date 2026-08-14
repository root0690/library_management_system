"""
Audit Service - READ ONLY access to audit logs.
Logs cannot be updated or deleted (enforced by DB triggers + this service).
"""

from database import execute_query


def get_audit_logs(limit=200, search=None):
    """
    Fetch audit logs (newest first).
    Optional search filters Action text or UserID.
    """
    try:
        if search and str(search).strip():
            term = f"%{str(search).strip()}%"
            return execute_query(
                """
                SELECT a.LogID, a.UserID, u.Username, a.Action, a.Timestamp
                FROM auditlogs a
                LEFT JOIN users u ON a.UserID = u.UserID
                WHERE a.Action LIKE %s OR CAST(a.UserID AS CHAR) LIKE %s OR u.Username LIKE %s
                ORDER BY a.Timestamp DESC, a.LogID DESC
                LIMIT %s
                """,
                (term, term, term, int(limit)),
                fetchall=True
            ) or []

        return execute_query(
            """
            SELECT a.LogID, a.UserID, u.Username, a.Action, a.Timestamp
            FROM auditlogs a
            LEFT JOIN users u ON a.UserID = u.UserID
            ORDER BY a.Timestamp DESC, a.LogID DESC
            LIMIT %s
            """,
            (int(limit),),
            fetchall=True
        ) or []
    except Exception as e:
        print(f"Error loading audit logs: {e}")
        return []


def get_audit_log_count():
    try:
        row = execute_query("SELECT COUNT(*) as cnt FROM auditlogs", fetchone=True)
        return row["cnt"] if row else 0
    except Exception:
        return 0
