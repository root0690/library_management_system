# Library Management System

Desktop application for managing library operations.

## Technology Stack
- Python 3.x
- CustomTkinter (GUI)
- MySQL (database)
- mysql-connector-python

## Features
- Secure login with role-based access (Administrator / Librarian)
- Book inventory management (Add / Edit / Delete / Search)
- Student management
- Issue & Return books
- Automatic fine calculation
- Reports (Inventory, Overdue, Transactions, Student Activity)
- Database backup
- Audit logging

## Setup

### 1. Create the MySQL database
Run the script:
```
database/schema_mysql.sql
```
in MySQL Workbench / phpMyAdmin.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure database password
Open `config.py` and write your MySQL password:
```python
DB_PASSWORD = "your_password_here"
```

### 4. Run the application
```bash
python main.py
```

## Default Login
- **Username:** admin  
- **Password:** admin123

## Project Structure
```
LibraryManagementSystem/
├── main.py
├── config.py
├── database.py
├── database/
│   └── schema_mysql.sql
├── gui/
│   ├── login.py
│   ├── dashboard.py
│   ├── books.py
│   ├── students.py
│   ├── issue_book.py
│   ├── return_book.py
│   ├── reports.py
│   └── settings.py
├── services/
│   ├── auth_service.py
│   ├── book_service.py
│   ├── student_service.py
│   ├── transaction_service.py
│   ├── fine_service.py
│   └── report_service.py
├── utils/
│   ├── hash_utils.py
│   ├── date_utils.py
│   └── validators.py
├── reports/
├── backups/
├── logs/
└── requirements.txt
```

## User Roles
| Feature              | Administrator | Librarian |
|----------------------|---------------|-----------|
| Login                | Yes           | Yes       |
| Manage Books         | Yes           | Yes       |
| Manage Students      | Yes           | Yes       |
| Issue / Return Books | Yes           | Yes       |
| View Reports         | Yes           | Yes       |
| Settings & Backup    | Yes           | No        |
