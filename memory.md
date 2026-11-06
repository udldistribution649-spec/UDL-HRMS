# UDL-HRMS — Project Memory

**Project:** UDL Human Resource Management System  
**Last Updated:** 6 November 2026  
**Purpose:** Persistent project decisions, development history and current implementation status.

---

# 1. Project Overview

UDL-HRMS is a custom Human Resource Management System being developed to replace the existing HRMS.

The project is inspired by the functional approach of Odoo HRMS but does not use Odoo itself.

The system is being developed with:

- Python 3.12
- FastAPI
- PostgreSQL 18
- SQLAlchemy
- Alembic
- Pydantic
- Pytest

Planned frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

The project will have two separate frontend applications:

1. Admin Portal
2. Employee Self-Service Portal

Both will use one centralized backend.

# 2. Development Environment

## Project Location

`E:\UDL-HRMS`

Backend:

`E:\UDL-HRMS\backend`

## Operating System

Windows 10.

## Database Environment

PostgreSQL 18.6.

PostgreSQL installation:

`E:\PostgreSQL\18`

Service:

`postgresql-x64-18`

Port:

`5432`

## Databases

| Database | Purpose |
|---|---|
| udl_hrms_db | Main development database |
| udl_hrms_test_db | Automated testing database |

Database user:

`udl_hrms_app`

Environment files:

- `.env` — main development configuration
- `.env.test` — test database configuration

Tests must use the test database, never the main database.

Test environment can be selected through:

`HRMS_ENV_FILE`

Before database tests, verify that:

`settings.DB_NAME == "udl_hrms_test_db"`

## Python Environment

Python version:

`3.12.10`

Virtual environment:

`E:\UDL-HRMS\backend\.venv`

Activation command:

```powershell
.\.venv\Scripts\Activate.ps1
```

Important installed packages include:

- FastAPI
- SQLAlchemy
- Alembic
- PyJWT
- pwdlib[argon2]
- openpyxl
- python-multipart
- pytest

# 3. Database and Migration History

Alembic is used for database schema management.

Migration script location:

`backend/migrations`

Current known migration history:

| Revision | Purpose |
|---|---|
| f57c2ae88210 | Initial HRMS schema |
| ed29245cca30 | Employee assignment history |
| b9e2c7d14a61 | Assignment history and nullable root employee manager |

Last verified migration head:

`b9e2c7d14a61 (head)`

The root employee is allowed to have a NULL reporting manager.

All future schema changes must use Alembic migrations.

Never modify the main database schema directly without explicit authorization and a migration plan.

# 4. Confirmed Business Decisions

Detailed business rules are maintained in `Rules.md`.

Important decisions:

## Employee

- Employee Code is numeric only.
- Maximum Employee Code length is 20 characters.
- Employee Codes are unique.
- New Employee Codes are generated automatically.
- Imported Employee Codes must be preserved.
- Rejoining employees receive new Employee Codes.
- Reporting Manager Code `0` means NULL.
- Only the root employee may have no reporting manager.
- Resigned employees remain preserved as inactive records.
- Historical data must not be fabricated.
- Missing historical Joining Dates remain blank.

## Organization

Hierarchy:

Location → Division → Department → Sub-Department

Other masters:

- Designation
- Grade Type
- Grade
- Sub-Grade

Automatic code formats:

- Location: `LOC-0001`
- Division: `DIV-0001`
- Department: `DEP-0001`
- Sub-Department: `SUB-0001`
- Designation: `DES-0001`

Department codes are unique within their Division.

Sub-Department codes are unique within their Department.

Grade Type, Grade and Sub-Grade do not currently require generated codes.

## Governance

- Director defines company-level authority where applicable.
- HR Admin manages HR operations and role assignments within approved policy.
- Super Admin represents IT Developer / IT Manager technical authority.
- Super Admin is not unrestricted policy authority.
- Director approval is optional/configurable where specified.
- Department Manager access is restricted to assigned organizational scopes.

## Security

- Email OTP two-factor authentication for all users.
- 15-minute session timeout.
- Secure password hashing.
- Mandatory first-login password change by default.
- Sensitive actions must be audited.

# 5. Current Backend Implementation

## Backend Foundation

Implemented foundations include:

- FastAPI application.
- PostgreSQL connection.
- SQLAlchemy database layer.
- Alembic migrations.
- Application configuration.
- API routing.
- Employee model foundation.
- Organization models.
- Authentication foundation.
- Security foundation.
- Audit logging foundation.

## Employee Module

Implemented foundations:

- Employee model.
- Employee API foundation.
- Employee Code validation.
- Numeric Employee Code generation.
- Employee assignment history.
- Nullable reporting manager for root employee.

## Organization Module

Implemented:

- Location APIs.
- Division APIs.
- Department APIs.
- Sub-Department APIs.
- Designation APIs.
- Grade Type APIs.
- Grade APIs.
- Sub-Grade APIs.
- Parent-child validation.
- Organization master code generation.
- Activation/deactivation foundations.

## Organization Code Generation

Service file:

`backend/app/services/organization_code_service.py`

The service generates:

- LOC codes globally.
- DIV codes globally.
- DEP codes per Division.
- SUB codes per Department.
- DES codes globally.

PostgreSQL advisory transaction locks are used to protect concurrent code generation.

The API schemas do not require HR Admin to submit generated codes.

## Department Manager Scope

Implemented foundations include:

- Scope request creation.
- Scope approval/rejection decision.
- Approved request execution.
- Scope listing.
- Organizational access restrictions.

Known API routes:

```text
/api/v1/department-manager-scopes/requests
/api/v1/department-manager-scopes/requests/{request_id}/decision/{decision}
/api/v1/department-manager-scopes/requests/{request_id}/execute
/api/v1/department-manager-scopes/
```

# 6. Test History

Previously reported successful test runs:

| Test Area | Result |
|---|---:|
| Organization API tests | 40 passed |
| Backend tests excluding interactive test_db.py | 60 passed |
| Organization concurrency tests | 2 passed |
| PF-related tests | 2 passed |
| Encryption tests | 2 passed |

These are results from separate test runs. They must not be combined into one claimed test result.

The interactive `test_db.py` is excluded from the regular non-interactive test run until its handling is addressed.

Always run relevant tests after modifying code.

Never claim a test passed without checking its actual output.

# 7. Important Historical Import Decisions

The existing employee dataset contained:

- 1,686 employees.
- 1,686 unique Employee Codes.
- 1,674 active employees.
- 12 resigned employees.

The 12 resigned employees must remain preserved as inactive records.

Their missing Joining Dates must remain blank.

No dates may be invented or backfilled.

Historical employee codes must remain unchanged.

# 8. Project Documentation

The following documents define the project baseline:

| File | Responsibility |
|---|---|
| PRD.md | Product requirements |
| Rules.md | Business rules |
| architect.md | Technical architecture |
| Task.md | Development task tracker |
| memory.md | Project decisions and development history |

When a confirmed project decision changes, update the appropriate document.

Do not allow these documents to contradict each other.

# 9. Pending Development Work

The following modules still require implementation or completion:

## Employee Management

- Complete Employee Master fields.
- Employee import.
- Employee profile change workflow.
- Historical data import.

## HR Operations

- Attendance.
- Leave.
- Complete approval workflows.
- Notifications.

## Payroll and PF

- Salary structures.
- Payroll calculations.
- Payroll processing.
- Salary slips.
- PF contributions.
- PF loans.
- PF withdrawals.
- PF profit calculations.
- EOBI and ESSI.

## Frontend

- Admin Portal.
- Employee Self-Service Portal.
- API integration.
- Role-based navigation.
- English and Urdu interface.

## Reporting and Deployment

- Management dashboards.
- HR reports.
- Payroll reports.
- Attendance reports.
- PF reports.
- Backup and recovery.
- Production deployment.
- End-to-end testing.

# 10. Development Safety Rules

These rules must be followed throughout development:

1. Preserve existing application functionality.
2. Preserve existing database records.
3. Never run destructive operations on the main database without explicit approval.
4. Use the test database for automated testing.
5. Verify database configuration before running tests.
6. Use Alembic for schema changes.
7. Review migrations before applying them.
8. Do not fabricate historical information.
9. Do not silently overwrite existing records.
10. Keep sensitive operations auditable.
11. Run relevant tests after code changes.
12. Update documentation when important decisions change.

# 11. Development Assistance Preferences

When providing coding instructions:

- Use Roman Urdu explanations.
- Keep instructions concise and beginner-friendly.
- Mention the exact file path.
- Identify exactly where code must be inserted or replaced.
- Prefer complete replacement code when practical.
- Avoid ambiguous indentation instructions.
- Do not ask for the same file repeatedly when its contents are already available.
- Work one clear step at a time.
- Wait for confirmation before assuming changes have been applied.
- Do not move to the next step until the current step is verified when verification is necessary.

# 12. Current Project Position

As of 6 November 2026:

- Backend foundation exists.
- Database connection is established.
- Initial migrations are applied.
- Employee and organization foundations exist.
- Organization automatic code generation is implemented.
- Concurrency protection has been tested.
- Department Manager scope workflow foundation exists.
- Project documentation baseline is being completed.

The project is still under development.

A module must not be marked complete merely because its database model or basic API exists. Its business rules, validation, authorization, workflows and tests must also be verified.

---

**End of Project Memory**

# 13. Original SRS Preservation and Pending Decisions

The original detailed SRS remains the source for functional requirements unless a later, explicit and authorized decision supersedes a requirement. Do not drop an SRS requirement merely because it is not yet implemented in the current backend.

The corrected PRD restores recruitment, resignation/withdrawal, termination/Show Cause, rejoining, attendance rosters/overtime/outstation, leave accrual/carry-forward/encashment, payroll benefits, PF Trustee, Full & Final Settlement, employee documents/letters, expanded ESS, notifications, dashboards and operational requirements.

## Pending policy items — do not assume

- PF Employee and Company shares: original SRS states 8.33% each; confirm current rates and salary base.
- PF Temporary and Third Party eligibility: original SRS lists both as ineligible; later draft explicitly lists only Contractual and Intern. Confirm.
- Zakat rate and calculation base: pending verification; do not hard-code 1.25% until approved.
- Employment status catalogue: current PRD lists Active, Resigned, Terminated and Retired; original SRS also mentions On Probation, On Notice, Deceased and On Hold. Confirm whether these are statuses or lifecycle flags.
- Leave accrual, carry-forward, expiry, encashment and probation eligibility.
- Tax method and current FBR values.
- EOBI/ESSI applicability and contribution calculations.
- Fuel litre carry-forward.
- Eidi and annual bonus cut-offs/eligibility.
- Overtime formula and special shift exceptions.
- PF Trustee authority, PF profit during active loan and retired employee transfer.
- Full & Final formula and approval authority.
- Excel template, source mapping and historical import coverage.
- Notification reminder intervals and performance/load targets.

## Requirements precedence

1. Later explicit user-approved business decisions supersede conflicting older SRS rules.
2. Where no later decision exists, preserve the original SRS requirement.
3. Where the sources conflict or approval is missing, label the point Pending Business Approval.
4. Technical documentation must not independently create company policy.
5. Never fabricate historical employee or transaction data.
