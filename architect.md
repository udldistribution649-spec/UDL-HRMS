# UDL-HRMS — System Architecture

**Project:** UDL Human Resource Management System
**Document:** Technical Architecture
**Version:** 1.0
**Last Updated:** 6 November 2026
**Status:** Architecture Foundation — In Progress

---

## 1. Project Overview

UDL-HRMS is a modular Human Resource Management System designed to replace the existing HRMS and provide an integrated employee management platform.

The system will provide:

- Employee Master Management
- Organization Structure Management
- Attendance Management
- Leave Management
- Payroll Management
- Provident Fund (PF) Management
- Employee Self-Service (ESS)
- Approval Workflows
- Employee Data Import
- Reports and Dashboards
- Audit Logs and Security
- Notifications

The system will be hosted locally and will use a centralized PostgreSQL database.

## 2. Technology Stack

### Backend

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL 18 |
| Database Migrations | Alembic |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Data Validation | Pydantic |
| Excel Processing | OpenPyXL |
| API Documentation | OpenAPI / Swagger |
| Testing | Pytest |

### Frontend — Planned

| Component | Technology |
|---|---|
| Framework | React |
| Language | TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| UI Components | shadcn/ui |

Admin Portal will be developed first. ESS will be a separate frontend application.

## 3. High-Level Architecture

The application will follow a modular architecture.

```text
                 ADMIN PORTAL
                       |
                       |
                  ESS PORTAL
                       |
                       v
                 FASTAPI BACKEND
                       |
          +------------+------------+
          |            |            |
       API Layer   Service Layer  Security
          |            |            |
          +------------+------------+
                       |
                  SQLAlchemy ORM
                       |
                  PostgreSQL DB
                       |
              Local Database Server
```

Both frontends will communicate with the backend through secured APIs.

Business rules will be implemented in the backend rather than duplicated in frontend applications.

## 4. Project Directory Structure

Project root:

```text
E:\UDL-HRMS
│
├── PRD.md
├── Rules.md
├── architect.md
├── Task.md
├── memory.md
│
├── backend
│   ├── app
│   │   ├── api
│   │   │   └── v1
│   │   │       └── endpoints
│   │   │
│   │   ├── core
│   │   ├── models
│   │   ├── schemas
│   │   ├── services
│   │   ├── repositories
│   │   ├── utils
│   │   └── main.py
│   │
│   ├── migrations
│   ├── scripts
│   ├── test
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env
│   └── .env.test
│
├── admin-portal        (Planned)
│
└── ess-portal          (Planned)
```

New modules must follow the existing structure. Do not create duplicate models, services, or database tables for functionality that already exists.

## 5. Backend Architecture

The backend follows a layered architecture.

### 5.1 API Layer

Location:

`backend/app/api/v1/endpoints/`

Responsibilities:

- Receive HTTP requests.
- Validate incoming data.
- Apply authentication and authorization dependencies.
- Call the relevant service functions.
- Return appropriate API responses.

API endpoints should not contain complex business logic.

### 5.2 Schema Layer

Location:

`backend/app/schemas/`

Responsibilities:

- Request validation.
- Response serialization.
- Field constraints.
- Input and output data structures.

Pydantic schemas must remain separate from SQLAlchemy models.

### 5.3 Model Layer

Location:

`backend/app/models/`

Responsibilities:

- Define database tables.
- Define relationships.
- Define database constraints.
- Define indexes and foreign keys.

Existing models should be reused wherever possible.

### 5.4 Service Layer

Location:

`backend/app/services/`

Responsibilities:

- Business rules.
- Approval processing.
- Employee assignment history.
- Organization code generation.
- Data validation.
- Transaction-related operations.

Services should be reusable by API endpoints and other backend modules.

### 5.5 Core Layer

Location:

`backend/app/core/`

Responsibilities:

- Database connection.
- Application configuration.
- Authentication and security.
- Shared application settings.

### 5.6 Repository Layer

Location:

`backend/app/repositories/`

Purpose:

- Centralize complex database queries.
- Separate data access from business logic when required.

Introduce repository functions where they provide a clear benefit; avoid unnecessary duplication.

## 6. Database Architecture

### Database Environment

| Environment | Database |
|---|---|
| Development | `udl_hrms_db` |
| Testing | `udl_hrms_test_db` |

Database technology: PostgreSQL 18.

SQLAlchemy is used for database operations.

Alembic is used for schema migrations.

### Database Rules

1. Never make unapproved schema changes directly in the main database.
2. Test migrations against the test database first.
3. Preserve existing employee and organization records.
4. Use foreign keys for related records.
5. Apply appropriate unique constraints and indexes.
6. Use transactions for operations involving multiple database changes.
7. Do not delete historical employee information without an approved business requirement.
8. Keep development and testing database configurations separate.

### Migration Management

Migration files are maintained in:

`backend/migrations/`

Current applied migration head:

`b9e2c7d14a61`

New schema changes must be managed through Alembic migrations.

## 7. Organization Master Architecture

Organization masters include:

- Location
- Division
- Department
- Sub-Department
- Designation
- Grade Type
- Grade
- Sub-Grade

### Automatic Code Generation

The backend generates codes automatically.

| Master | Prefix | Sequence |
|---|---|---|
| Location | LOC | Global |
| Division | DIV | Global |
| Department | DEP | Per Division |
| Sub-Department | SUB | Per Department |
| Designation | DES | Global |

Example:

```text
LOC-0001
DIV-0001
DEP-0001
SUB-0001
DES-0001
```

HR Admin does not manually enter these codes.

PostgreSQL advisory transaction locks are used to protect code generation against simultaneous creation requests.

Department codes are unique within their parent Division.

Sub-Department codes are unique within their parent Department.

Grade Type, Grade and Sub-Grade currently do not have generated code fields.

## 8. Employee Management Architecture

Employee Management is a central module.

Responsibilities:

- Employee creation and maintenance.
- Employee code generation.
- Employee profile.
- Employment status.
- Organization assignment.
- Reporting manager assignment.
- Employee history.
- Employee rejoining.
- Employee data import.

### Employee Code Rules

- Employee codes are numeric.
- Existing company-generated employee codes must be preserved during imports.
- New employees receive automatically generated codes.
- Rejoining employees receive a new employee code.
- A root employee may have no reporting manager.
- Reporting manager code `0` is treated as NULL.

### Assignment History

Employee organization and reporting-manager changes must maintain historical records.

The `EmployeeAssignmentHistory` model stores assignment history separately from the Employee Master record.

## 9. Security Architecture

Security must be enforced at the backend API and service layers.

### Roles

- Super Admin
- HR Admin
- Director
- Department Manager
- Payroll Manager

### Security Responsibilities

**Super Admin**

- IT-level technical administration.
- Backend and configuration maintenance.
- Authorized session management.
- Server-side backup operations.

Super Admin is not unrestricted company policy authority.

**HR Admin**

- Employee administration.
- Operational HR management.
- Role assignment within approved policy.
- Organization and workflow administration.

**Director**

- Company-level authority where approval is required by policy.
- Approval of configured workflows.

**Department Manager**

- Access to assigned departments and sub-departments.
- Approval and rejection within assigned authority.

**Payroll Manager**

- Payroll-related responsibilities within assigned permissions.

### Security Controls

- JWT-based authentication.
- Argon2 password hashing.
- Email OTP two-factor authentication.
- 15-minute session timeout.
- Role-based access control.
- Audit logs for sensitive actions.
- Mandatory password change where required.
- Session monitoring and termination by authorized Super Admin.

Permissions must be checked on the backend. Hiding frontend buttons is not an authorization mechanism.

## 10. Approval Workflow Architecture

Approval workflows will be managed centrally through backend services.

Department Manager access is restricted to assigned department and sub-department scopes.

Department Manager scope changes follow this process:

1. HR Admin initiates a scope request.
2. Director approval is obtained when configured as required.
3. The request is approved or rejected by the authorized person.
4. Only an approved request can be executed by authorized IT/Super Admin.
5. All sensitive actions are recorded in audit logs.

No self-approval is allowed.

PF Loan, PF Withdrawal and Company Loan retain their separate approval chains.

## 11. Planned Functional Modules

The following modules are part of the target architecture. Their implementation status must be tracked separately.

| Module | Purpose |
|---|---|
| Employee Master | Employee records and profiles |
| Organization | Organization structure |
| Employee Import | Excel and historical data import |
| Attendance | Attendance and working days |
| Leave | Leave balances and applications |
| Payroll | Salary calculation and processing |
| Provident Fund | PF contributions, loans and withdrawals |
| Approvals | Configurable approval workflows |
| Notifications | In-app and email notifications |
| Reports | HR and management reporting |
| Backup | Server-side database backup |
| ESS | Employee self-service |

## 12. Employee Data Import Architecture

Import functionality will support:

- Excel employee import.
- Historical employee records.
- Historical attendance.
- Historical payroll.
- Leave balances and history.
- PF historical records.

### Import Process

```text
Excel / Source Database
          |
          v
    Read Source Data
          |
          v
     Validate Data
          |
          v
      Preview
          |
          v
     Confirm Import
          |
          v
   Atomic Database Import
          |
          v
    Import Audit Log
```

### Import Rules

- Preserve original employee codes.
- Validate duplicate records.
- Validate organization references.
- Validate reporting managers.
- Do not silently overwrite existing records.
- Use all-or-nothing transactions.
- Provide validation errors before final import.
- Support corrected full re-imports where applicable.

### External Database Import

Future source database support:

- PostgreSQL
- Microsoft SQL Server
- MySQL

Source database credentials must be encrypted.

Connections must use read-only database permissions.

## 13. Frontend Architecture

### Admin Portal

The Admin Portal will be developed first.

Expected functionality:

- Dashboard.
- Employee management.
- Organization masters.
- Attendance management.
- Leave management.
- Payroll.
- PF.
- Approval management.
- Reports.
- User and role administration.

Frontend technology:

React, TypeScript, Vite, Tailwind CSS and shadcn/ui.

### ESS Portal

ESS will be developed as a separate frontend application.

Expected functionality:

- Employee login.
- Own profile viewing.
- Attendance information.
- Leave applications.
- Salary slips.
- PF information.
- Notifications.
- Profile change requests.

Employees must only access their own permitted information.

## 14. Testing Architecture

Testing framework: Pytest.

Test database:

`udl_hrms_test_db`

Testing principles:

1. Never run destructive tests against the main database.
2. Verify database configuration before test execution.
3. Use independent transactions where concurrency is being tested.
4. Test API permissions and validation.
5. Test database constraints.
6. Test business rules.
7. Test migration compatibility.
8. Clean up test-created records where transactions are committed.

### Verified Test Results

As of 6 November 2026:

- Organization API tests: 40 passed.
- Backend tests excluding interactive `test_db.py`: 60 passed.
- Organization code concurrency tests: 2 passed.

Concurrency verification included 10 simultaneous Department creations and 10 simultaneous Sub-Department creations.

These results represent separate test runs, not a single combined test run.

## 15. Backup and Recovery Architecture

Planned backup responsibilities:

- Server-side database backups.
- Daily backup scheduling.
- 30-day backup retention.
- Restricted backup access.
- Recovery procedure documentation.

Backup and restore operations must be verified before production use.

## 16. Development and Change Management Rules

1. Preserve existing working functionality.
2. Do not replace complete modules without reviewing dependencies.
3. Inspect existing code before introducing new files.
4. Do not create duplicate models or tables.
5. Use Alembic for database schema changes.
6. Test changes using the test database.
7. Keep business rules in backend services.
8. Keep authorization checks on the backend.
9. Record important architectural decisions in `memory.md`.
10. Update `Task.md` when implementation status changes.
11. Update `Rules.md` when business rules are approved or changed.
12. Update `PRD.md` when functional requirements change.

## 17. Additional Planned Module Architecture

The target architecture must also account for the following business modules from the original SRS:

- Recruitment and candidate lifecycle.
- Resignation, resignation withdrawal and termination/Show Cause.
- Rejoining and linked employment episodes.
- Attendance shifts, rosters, correction, outstation requests and monthly close.
- Leave accrual, carry-forward, expiry and encashment.
- Payroll allowances, fuel, Eidi, annual bonus, tax and statutory deductions.
- Separate Employee and Company PF ledgers, PF Trustee workflow, loan and withdrawal.
- Full & Final Settlement.
- Employee documents and official letters.
- ESS-specific approval scopes, separate from HRMS manager scopes.
- In-app/email notifications and approved HR announcements.
- Management dashboards and role-restricted reports.

These are planned functional capabilities, not claims that their backend implementation already exists.

### Architecture boundaries

- HRMS backend/database remains the authoritative employee and transaction record.
- Admin Portal and ESS are separate frontend applications using secured APIs.
- ESS manager approval scopes are independently configured; they are not automatically copied from HRMS Department Manager scopes.
- Source database import adapters must use read-only credentials and encrypted secrets.
- Audit records must preserve actor, action, timestamp, reason and old/new values where applicable.
- Business policy values must be configurable where required and must not be invented by technical implementation.

## 18. Current Implementation Status

### Implemented Foundation

- FastAPI application foundation.
- PostgreSQL database connectivity.
- SQLAlchemy models and database session management.
- Alembic migrations.
- Employee Master foundation.
- Organization master APIs.
- Employee assignment history.
- Root employee manager NULL support.
- Authentication foundation.
- Role and permission foundation.
- Audit logging foundation.
- Department Manager scope request foundation.
- Organization master automatic code generation.
- PostgreSQL advisory-lock-based code generation concurrency protection.
- Test database protection in relevant tests.

### Pending / Incomplete

- Complete Employee Import module.
- Complete historical data import.
- Complete Attendance module.
- Complete Leave module.
- Complete Payroll module.
- Complete PF module.
- Complete ESS application.
- Complete Admin Portal.
- Full notification implementation.
- Complete reporting and dashboards.
- Production backup and recovery implementation.
- Full end-to-end workflow verification.

Implementation status must be updated as each module is completed and tested.

## 19. Relationship Between Project Documents

| Document | Responsibility |
|---|---|
| `PRD.md` | What the system must do |
| `Rules.md` | Approved business rules |
| `architect.md` | How the system is technically designed |
| `Task.md` | What is completed and what remains |
| `memory.md` | Important decisions and development progress |

All six documents must remain consistent.

---

**End of Document**
