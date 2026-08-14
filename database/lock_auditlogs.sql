-- ============================================================
-- Make auditlogs IMMUTABLE
-- Run this once in MySQL Workbench
-- ============================================================

USE library_management;

-- Block UPDATE on auditlogs
DROP TRIGGER IF EXISTS prevent_auditlog_update;
DELIMITER //
CREATE TRIGGER prevent_auditlog_update
BEFORE UPDATE ON auditlogs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Audit logs are immutable. UPDATE is not allowed.';
END//
DELIMITER ;

-- Block DELETE on auditlogs
DROP TRIGGER IF EXISTS prevent_auditlog_delete;
DELIMITER //
CREATE TRIGGER prevent_auditlog_delete
BEFORE DELETE ON auditlogs
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Audit logs are immutable. DELETE is not allowed.';
END//
DELIMITER ;

-- Block TRUNCATE via a safeguard note:
-- MySQL does not fire triggers on TRUNCATE.
-- Do NOT run: TRUNCATE TABLE auditlogs;

SELECT 'Audit log immutability triggers installed successfully.' AS Message;
