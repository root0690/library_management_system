-- Library Management System Database Schema
-- SQLite

PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    UserID      INTEGER PRIMARY KEY AUTOINCREMENT,
    Username    TEXT    NOT NULL UNIQUE,
    PasswordHash TEXT   NOT NULL,
    Role        TEXT    NOT NULL CHECK(Role IN ('Administrator', 'Librarian')),
    CreatedAt   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    BookID            INTEGER PRIMARY KEY AUTOINCREMENT,
    ISBN              TEXT    UNIQUE,
    Title             TEXT    NOT NULL,
    Author            TEXT    NOT NULL,
    Category          TEXT,
    Quantity          INTEGER NOT NULL DEFAULT 1 CHECK(Quantity >= 0),
    AvailableQuantity INTEGER NOT NULL DEFAULT 1 CHECK(AvailableQuantity >= 0)
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    StudentID   INTEGER PRIMARY KEY AUTOINCREMENT,
    Name        TEXT    NOT NULL,
    Department  TEXT,
    Semester    TEXT,
    Phone       TEXT
);

-- Issues (transactions) table
CREATE TABLE IF NOT EXISTS issues (
    IssueID     INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID      INTEGER NOT NULL,
    StudentID   INTEGER NOT NULL,
    IssueDate   TEXT    NOT NULL,
    DueDate     TEXT    NOT NULL,
    ReturnDate  TEXT,
    Fine        REAL    DEFAULT 0,
    Status      TEXT    NOT NULL DEFAULT 'Issued' CHECK(Status IN ('Issued', 'Returned')),
    FOREIGN KEY (BookID)    REFERENCES books(BookID),
    FOREIGN KEY (StudentID) REFERENCES students(StudentID)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS auditlogs (
    LogID     INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID    INTEGER,
    Action    TEXT    NOT NULL,
    Timestamp TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_books_title ON books(Title);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(ISBN);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(Name);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(Status);
CREATE INDEX IF NOT EXISTS idx_auditlogs_timestamp ON auditlogs(Timestamp);
