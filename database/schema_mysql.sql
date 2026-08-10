-- ============================================================
-- Library Management System - MySQL Database Schema
-- Run this script in your MySQL software (MySQL Workbench,
-- phpMyAdmin, MySQL Command Line, etc.)
-- ============================================================

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS library_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Use the database
USE library_management;

-- 3. Users table
CREATE TABLE IF NOT EXISTS users (
    UserID       INT AUTO_INCREMENT PRIMARY KEY,
    Username     VARCHAR(50)  NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role         ENUM('Administrator', 'Librarian') NOT NULL,
    CreatedAt    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Books table
CREATE TABLE IF NOT EXISTS books (
    BookID            INT AUTO_INCREMENT PRIMARY KEY,
    ISBN              VARCHAR(20) UNIQUE,
    Title             VARCHAR(255) NOT NULL,
    Author            VARCHAR(150) NOT NULL,
    Category          VARCHAR(100),
    Quantity          INT NOT NULL DEFAULT 1 CHECK (Quantity >= 0),
    AvailableQuantity INT NOT NULL DEFAULT 1 CHECK (AvailableQuantity >= 0)
) ENGINE=InnoDB;

-- 5. Students table
CREATE TABLE IF NOT EXISTS students (
    StudentID  INT AUTO_INCREMENT PRIMARY KEY,
    Name       VARCHAR(150) NOT NULL,
    Department VARCHAR(100),
    Semester   VARCHAR(20),
    Phone      VARCHAR(20)
) ENGINE=InnoDB;

-- 6. Issues (transactions) table
CREATE TABLE IF NOT EXISTS issues (
    IssueID    INT AUTO_INCREMENT PRIMARY KEY,
    BookID     INT NOT NULL,
    StudentID  INT NOT NULL,
    IssueDate  DATE NOT NULL,
    DueDate    DATE NOT NULL,
    ReturnDate DATE NULL,
    Fine       DECIMAL(10,2) DEFAULT 0.00,
    Status     ENUM('Issued', 'Returned') NOT NULL DEFAULT 'Issued',
    FOREIGN KEY (BookID)    REFERENCES books(BookID) ON DELETE RESTRICT,
    FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 7. Audit logs table
CREATE TABLE IF NOT EXISTS auditlogs (
    LogID     INT AUTO_INCREMENT PRIMARY KEY,
    UserID    INT NULL,
    Action    VARCHAR(255) NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES users(UserID) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Useful indexes
CREATE INDEX idx_books_title ON books(Title);
CREATE INDEX idx_books_isbn ON books(ISBN);
CREATE INDEX idx_students_name ON students(Name);
CREATE INDEX idx_issues_status ON issues(Status);
CREATE INDEX idx_auditlogs_timestamp ON auditlogs(Timestamp);

-- ============================================================
-- Optional: Insert a default admin user later from the app
-- (Password will be hashed by the Python application)
-- ============================================================

SELECT 'Database and tables created successfully!' AS Message;
