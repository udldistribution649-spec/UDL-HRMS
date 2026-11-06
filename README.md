# UDL-HRMS

**UDL Human Resource Management System**

A custom Human Resource Management System designed to centralize employee records, HR operations, attendance, leave, payroll, provident fund and employee self-service.

**Project Status:** Under Development

---

## 1. Project Overview

UDL-HRMS is being developed as a replacement for the existing HRMS.

The system uses a centralized backend and PostgreSQL database, with two planned frontend applications:

- Admin Portal
- Employee Self-Service (ESS) Portal

The project is inspired by Odoo HRMS functionality but does not use Odoo.

## 2. Technology Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL 18
- Alembic
- Pydantic
- JWT Authentication
- Argon2 Password Hashing

### Testing

- Pytest
- FastAPI TestClient

### Planned Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

## 3. Project Structure

```text
E:\UDL-HRMS
│
├── backend
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   ├── models
│   │   ├── schemas
│   │   ├── services
│   │   └── main.py
│   │
│   ├── migrations
│   ├── tests
│   ├── .env
│   ├── .env.test
│   ├── alembic.ini
│   └── requirements.txt
│
├── PRD.md
├── Rules.md
├── architect.md
├── Task.md
├── memory.md
└── README.md
```

This structure describes the current backend organization and project documentation. Additional folders will be added as development progresses.

## 4. Development Environment

Required software:

- Windows 10 or compatible environment
- Python 3.12
- PostgreSQL 18
- Visual Studio Code
- Git (planned for project version control)

## 5. Backend Setup

Open PowerShell and navigate to:

```powershell
cd E:\UDL-HRMS\backend
```

Activate the Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies if required:

```powershell
pip install -r requirements.txt
```

Ensure that the development `.env` file has the correct database configuration before starting the application.

Never share or commit database passwords, JWT secrets or encryption keys.

## 6. Run Backend

From the backend directory, activate the virtual environment and run:

```powershell
uvicorn app.main:app --reload
```

Expected local development address:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 7. Database Configuration

PostgreSQL database:

| Database | Purpose |
|---|---|
| udl_hrms_db | Main development database |
| udl_hrms_test_db | Automated testing database |

Database configuration is maintained through environment files.

- `.env` is used for main development.
- `.env.test` is used for test configuration through `HRMS_ENV_FILE`.

Do not use the main development database for automated test execution.

## 8. Database Migrations

Alembic manages database schema changes.

Check current migration:

```powershell
alembic current
```

Check migration history:

```powershell
alembic history
```

Apply reviewed migrations:

```powershell
alembic upgrade head
```

Always review migration scripts and verify the target database before applying migrations.

Never run unreviewed or destructive migrations against the main database.

## 9. Run Tests

Run the non-interactive backend tests:

```powershell
pytest -q --ignore=test_db.py
```

Before running tests:

1. Activate the virtual environment.
2. Load `.env.test` using the project's test configuration.
3. Verify that the active database is `udl_hrms_test_db`.
4. Run the tests.

Never assume that the test database is selected without verification.

## 10. Current Implementation

Known implemented foundations:

- FastAPI backend.
- PostgreSQL database connection.
- SQLAlchemy models.
- Alembic migrations.
- Employee Master foundation.
- Employee assignment history.
- Organization Master APIs.
- Automatic organization code generation.
- Concurrency protection for organization code generation.
- Authentication and security foundations.
- Department Manager scope workflow foundation.
- Initial audit logging foundation.

## 11. Planned Modules

- Complete Employee Management.
- Employee Import.
- Historical Data Import.
- Attendance Management.
- Leave Management.
- Complete Payroll.
- Provident Fund.
- EOBI and ESSI.
- Notifications.
- Admin Portal.
- Employee Self-Service Portal.
- Reports and Dashboards.
- Backup and Recovery.

## 12. Project Documentation

| File | Description |
|---|---|
| `PRD.md` | Product requirements |
| `Rules.md` | Business rules |
| `architect.md` | Technical architecture |
| `Task.md` | Development task tracker |
| `memory.md` | Important decisions and development history |
| `README.md` | Project introduction and setup instructions |

## 13. Development Guidelines

- Preserve existing application functionality.
- Do not delete historical employee records.
- Do not fabricate historical data.
- Use Alembic for schema changes.
- Use the test database for automated tests.
- Validate changes before applying them to the main database.
- Maintain audit history for sensitive operations.
- Update project documentation when important decisions change.

---

**UDL-HRMS — Human Resource Management System**

**Status:** Development In Progress

## 14. Requirements Baseline

The original detailed SRS requirements are preserved in `PRD.md`. Requirements that need management/HR confirmation are explicitly marked **Pending Business Approval** and must not be implemented using assumptions.

The six project documents are:
- `README.md`
- `PRD.md`
- `Rules.md`
- `architect.md`
- `Task.md`
- `memory.md`

`PRD.md` describes required functionality, `Rules.md` records approved business rules and pending policy clarifications, `architect.md` describes technical design, `Task.md` tracks implementation, and `memory.md` records project decisions and development history.
