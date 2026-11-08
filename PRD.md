# UDL-HRMS — Product Requirements Document (PRD)

**Project:** UDL Human Resource Management System
**Document:** Product Requirements Document
**Version:** 1.0
**Last Updated:** 6 November 2026
**Status:** Requirements Baseline — Implementation In Progress

---

# 1. Introduction

## 1.1 Purpose

UDL-HRMS is an integrated Human Resource Management System designed to replace the existing HRMS and centralize employee-related operations.

The system will manage employee records, organization structure, attendance, leave, payroll, provident fund, approvals, reporting and employee self-service.

The system will provide controlled access based on user roles, organizational responsibilities and approval authority.

## 1.2 Business Objectives

The primary objectives are:

1. Centralize employee information.
2. Replace manual HR operations with controlled workflows.
3. Maintain accurate employee and organizational records.
4. Automate attendance-based payroll processing.
5. Manage employee leave and provident fund.
6. Introduce role-based approvals.
7. Preserve historical employee and transaction data.
8. Provide Employee Self-Service.
9. Improve management reporting.
10. Maintain audit trails for sensitive operations.
11. Support historical data migration from existing systems.
12. Host the system locally under company control.

## 1.3 Product Scope

The product consists of two separate frontend applications and one centralized backend:

- Admin Portal
- Employee Self-Service (ESS) Portal
- Central FastAPI Backend

Both portals will communicate with the same backend and database through secured APIs.

---

# 2. Users and Roles

## 2.1 Super Admin

Represents IT Developer / IT Manager technical authority.

Responsibilities:

- Technical system administration.
- Backend and configuration maintenance.
- Authorized user session management.
- Server-side backup operations.
- Execution of approved administrative workflows.
- Technical troubleshooting.

Super Admin does not have unrestricted company policy authority.

## 2.2 HR Admin

Responsibilities:

- Employee Master administration.
- Employee profile management.
- Organization master administration.
- HR operational workflows.
- Employee data imports.
- Operational role assignments within approved policies.
- Initiation of Department Manager scope requests.
- HR reporting and dashboards.

## 2.3 Director

Responsibilities:

- Company-level authority where configured.
- Approval of workflows requiring Director approval.
- HR announcement approval.
- Management-level dashboards and reports.

Director approval is optional/configurable where specified by the applicable workflow policy.

## 2.4 Department Manager

Responsibilities:

- View assigned department/sub-department employees.
- Review and process assigned approvals.
- Approve or reject ordinary applications within assigned authority.
- View permitted departmental information.

Department Managers must not access unassigned organizational scopes.

## 2.5 Payroll Manager

Responsibilities:

- Payroll operations.
- Salary processing within assigned permissions.
- Payroll reports.
- Authorized payroll review and processing.

## 2.6 Employee

Responsibilities:

- Access own employee information.
- Submit permitted profile change requests.
- Submit leave applications.
- View permitted attendance information.
- View salary slips.
- View permitted PF information.
- Track submitted requests.

Employees must only access their own permitted records.

---

# 3. Organization Management Module

## 3.1 Purpose

Manage the company's organizational hierarchy and related master data.

## 3.2 Organization Hierarchy

Location → Division → Department → Sub-Department

Additional organization masters:

- Designation
- Grade Type
- Grade
- Sub-Grade

## 3.3 Functional Requirements

The system must allow authorized HR users to:

- Create organization master records.
- View organization master records.
- Update organization master records.
- Activate and deactivate records.
- Search and filter records.
- View parent-child relationships.
- Prevent invalid parent references.
- Preserve organization assignment history.

## 3.4 Automatic Code Generation

The system must automatically generate codes.

| Master | Format | Sequence |
|---|---|---|
| Location | LOC-0001 | Global |
| Division | DIV-0001 | Global |
| Department | DEP-0001 | Per Division |
| Sub-Department | SUB-0001 | Per Department |
| Designation | DES-0001 | Global |

Grade Type, Grade and Sub-Grade do not currently require generated code fields.

The system must prevent duplicate codes during simultaneous creation requests.

## 3.5 Acceptance Criteria

- HR Admin cannot manually submit generated codes.
- Backend generates valid codes.
- Department codes are unique within a Division.
- Sub-Department codes are unique within a Department.
- Invalid parent relationships are rejected.
- Referenced organization records cannot be deleted.
- Existing codes are preserved.

---

# 4. Employee Master Module

## 4.1 Purpose

Maintain a centralized and reliable employee record.

## 4.2 Employee Information

The Employee Master must support:

- Employee Code
- Employee Name
- CNIC
- Date of Birth
- Gender
- Contact Information
- Email Address
- Present Address
- Permanent Address
- Joining Date
- Employment Status
- Contract Type
- Location
- Division
- Department
- Sub-Department
- Designation
- Grade Type
- Grade
- Sub-Grade
- Reporting Manager
- Confirmation Information
- Other approved HR fields

Final field definitions must follow the approved employee data specification.

## 4.3 Employee Code Requirements

- Numeric characters only.
- Maximum 20 characters.
- Unique across employees.
- Automatically generated for new employees.
- Imported Employee Codes must be preserved.
- Rejoining employees receive a new Employee Code.
- Employee Code cannot be changed through ESS.

## 4.4 Employee Status

The currently documented status baseline is:

- Active
- Resigned
- Terminated
- Retired

Resigned employees must remain preserved as inactive records.

Historical employee information must not be deleted.

The original SRS also mentions On Probation, On Notice, Deceased and On Hold. These may be employment statuses or separate lifecycle flags. HR must confirm their classification before they are added to the final status catalogue. Do not silently discard these requirements or implement them as final values without approval.

## 4.5 Contract Types

- Permanent
- Contractual
- Probation
- Intern
- Third Party
- Temporary

## 4.6 Reporting Manager

- Each employee must have a valid reporting manager except the root employee.
- Root employee may have NULL reporting manager.
- Reporting Manager Code `0` represents NULL during imports.
- Self-reporting is not allowed.
- Invalid manager references must be rejected.
- Reporting manager changes must maintain history.

## 4.7 Employee Rejoining

The system must:

- Preserve previous employment records.
- Generate a new Employee Code.
- Record the new employment event.
- Maintain previous service history.
- Re-evaluate applicable PF eligibility.

## 4.8 Employee Assignment History

The system must maintain previous and new values for:

- Location
- Division
- Department
- Sub-Department
- Designation
- Grade
- Reporting Manager

History must include effective date, responsible user and reason.

## 4.9 Acceptance Criteria

- Employee Code uniqueness is enforced.
- Required fields are validated.
- Organization references are validated.
- Reporting manager rules are enforced.
- Historical assignment information remains available.
- Employee deactivation does not delete the record.

---

# 5. Employee Profile Change Module

## 5.1 Purpose

Allow employees to request changes to permitted personal information without directly modifying protected employee records.

## 5.2 Functional Requirements

The system must allow employees to:

- View their own profile.
- Submit permitted profile change requests.
- Provide supporting documents.
- View request status.
- View approval or rejection results.

HR must be able to:

- Review requests.
- Approve requests.
- Reject requests with a reason.
- View old and requested values.

Approved changes must update the Employee Master through an authorized workflow.

Salary, PF and organizational changes must follow separate workflows.

---

# 6. Authentication and Access Control

## 6.1 Login

The system must provide secure login for authorized users.

ESS login:

- Employee Code
- Password

Administrative login must follow the configured account identity and authentication policy.

## 6.2 Security Requirements

- JWT-based authentication.
- Secure password hashing.
- Email OTP two-factor authentication for all users.
- 15-minute session timeout.
- Mandatory password change by default on first login.
- Secure password reset.
- Role-based access control.
- Organizational scope-based access.
- Audit logging for sensitive actions.

## 6.3 Session Management

Authorized Super Admin must be able to:

- View active sessions.
- Terminate sessions.

Session operations must be restricted and auditable.

## 6.4 Acceptance Criteria

- Unauthorized users cannot access protected APIs.
- Users cannot exceed assigned permissions.
- Department Managers cannot access unassigned departments.
- Employees cannot access other employees' records.
- Expired sessions must not remain usable.

---

# 7. Department Manager Scope Management

## 7.1 Purpose

Control which departments and sub-departments a Department Manager can access and manage.

## 7.2 Functional Requirements

HR Admin must be able to initiate:

- New scope assignment.
- Scope change.
- Scope revocation.

Workflow:

1. HR Admin submits request.
2. Director approval is obtained if configured as required.
3. Authorized person approves or rejects.
4. Approved request becomes eligible for execution.
5. Authorized Super Admin / IT executes the approved request.

## 7.3 Restrictions

- HR Admin cannot directly activate a scope.
- Self-approval is not allowed.
- Managers only access assigned scopes.
- Scope changes must be auditable.

## 7.4 Acceptance Criteria

- Unapproved requests cannot be executed.
- Rejected requests cannot be executed.
- Unauthorized execution is rejected.
- Manager access reflects approved scopes.

---

# 8. Attendance Management Module

## 8.1 Purpose

Manage employee attendance and provide verified attendance information for payroll processing.

## 8.2 Functional Requirements

The system must support:

- Daily attendance records.
- Monthly attendance processing.
- Employee attendance history.
- Attendance corrections.
- Authorized correction approvals.
- Attendance imports.
- Attendance reports.
- Attendance summaries.

## 8.3 Payroll Integration

- Payroll uses previous month's attendance.
- Attendance must be validated before payroll processing.
- Attendance must respect employee joining and leaving dates.

Detailed shift, overtime, late arrival and attendance calculation policies require separate approval.

## 8.4 Acceptance Criteria

- Attendance is linked to the correct employee.
- Duplicate or invalid records are handled through validation.
- Unauthorized corrections are rejected.
- Historical attendance remains available.

---

# 9. Leave Management Module

## 9.1 Purpose

Manage employee leave entitlements, applications, approvals and balances.

## 9.2 Leave Types

| Leave Type | Annual Entitlement |
|---|---:|
| Annual Leave | 15 days |
| Sick Leave | 10 days |
| Casual Leave | 10 days |

## 9.3 Functional Requirements

The system must support:

- Leave policy configuration.
- Leave balance management.
- Leave applications.
- Leave approvals.
- Leave rejection with reason.
- Leave history.
- Leave balance adjustments.
- Leave reports.

## 9.4 Acceptance Criteria

- Employees can submit permitted leave requests.
- Approval follows configured authority.
- Rejected applications do not reduce leave balance.
- Approved leave updates balance through authorized transactions.
- Leave history is retained.

Carry-forward, encashment and other detailed leave policies require approval.

---

# 10. Payroll Management Module

## 10.1 Purpose

Calculate and manage employee salaries through controlled payroll processing.

## 10.2 Payroll Period

Financial Year: July to June.

Current month salary uses previous month's attendance.

## 10.3 Functional Requirements

The system must support:

- Salary structures.
- Salary components.
- Earnings.
- Deductions.
- Attendance-based salary calculation.
- Monthly payroll processing.
- Payroll review and approval.
- Salary slips.
- Payroll history.
- Payroll reports.
- Historical payroll imports.

## 10.4 Employee Eligibility

Payroll processing must consider:

- Joining Date.
- Resignation Date.
- Termination Date.
- Employment Status.
- Applicable payroll period.

No eligible salary slip is generated for new joiners, resigned or terminated employees according to applicable payroll period rules.

## 10.5 Acceptance Criteria

- Salary calculations use approved components.
- Attendance period is correctly mapped.
- Payroll calculations retain their inputs and history.
- Payroll changes are authorized and audited.
- Salary slips are available only to authorized users and the relevant employee.

Tax, overtime, arrears, bonuses and final settlement specifications require separate approval.

---

# 11. Provident Fund Module

## 11.1 Purpose

Manage employee PF eligibility, contributions, balances, loans, withdrawals and profit.

## 11.2 Eligibility

- Contractual employees are PF-ineligible.
- Intern employees are PF-ineligible.
- PF starts according to confirmation eligibility.
- Rejoining employees must be evaluated under applicable PF rules.

## 11.3 Contribution Calculation

If confirmation occurs during the month:

Gross Salary / 30 × Eligible Work Days × 8.33%

Otherwise:

Gross Salary × 8.33%

## 11.4 PF Loan

- Maximum loan period: 48 months.
- Loan must follow a separate approval workflow.
- Repayment and outstanding balance must be maintained.
- Loan transactions must be auditable.

## 11.5 PF Withdrawal

- Normal withdrawal limit: 70%.
- Special approval may permit an exception.
- Zakat is 1.25% on eligible withdrawal and Final Settlement.
- Withdrawal must follow the separate approval workflow.

## 11.6 PF Profit

- Profit during active loans follows approved financial-year rules.
- Profit is not paid for the period affected by an active loan.
- Earlier months before the financial-year impact of the loan may be considered according to the approved calculation.
- Exact month-wise profit calculation must follow the approved PF specification.

## 11.7 PF Access

- PF information must be role-restricted.
- HR visibility is limited to PF loan information and PF balance according to assigned permissions.
- Employees may view only their permitted PF information.
- Unauthorized users must not access PF details.

## 11.8 Acceptance Criteria

- Eligibility is validated.
- Contribution calculation follows approved rules.
- PF balance is traceable.
- Loan and withdrawal transactions are auditable.
- Access restrictions are enforced.

---

# 12. EOBI and ESSI Management

The system must support:

- EOBI eligibility.
- ESSI eligibility.
- Registration numbers.
- Registration dates.
- Historical registration information.

Historical values must not be fabricated.

Detailed contribution and eligibility calculations require approved specifications.

---

# 13. Employee Data Import Module

## 13.1 Purpose

Migrate employee records and historical information from existing HR systems and Excel files.

## 13.2 Supported Import Types

- Employee Master.
- Historical Attendance.
- Historical Payroll.
- Leave History.
- PF History.

## 13.3 Excel Import Process

1. Upload Excel file.
2. Read and validate data.
3. Check duplicates.
4. Validate organization references.
5. Validate reporting managers.
6. Validate required fields.
7. Display import preview.
8. Show errors and warnings.
9. Confirm import.
10. Execute atomic import.
11. Record import audit history.

## 13.4 Import Rules

- Preserve original Employee Codes.
- Reject duplicate Employee Codes.
- Reject existing Employee Code conflicts.
- Do not silently overwrite existing employees.
- Validate all organization references.
- Resolve managers using Employee Code.
- Treat manager code `0` as NULL for root employee.
- Missing historical Joining Dates remain blank.
- Never fabricate historical data.
- Import must be all-or-nothing.
- Corrected re-import must not silently update existing employees.

## 13.5 External Database Import

Planned supported sources:

- PostgreSQL.
- Microsoft SQL Server.
- MySQL.

Requirements:

- Encrypted source credentials.
- Read-only source database access.
- Restricted access to source profiles.
- Connection testing.
- Data mapping.
- Validation preview.
- Atomic import.
- Import audit history.

## 13.6 Acceptance Criteria

- Invalid records are identified before import.
- Duplicate records are rejected.
- Valid records are imported without changing original Employee Codes.
- Failed imports do not leave partial data.
- Import activity is auditable.

---

# 14. Employee Self-Service Portal

## 14.1 Purpose

Provide employees with secure access to their own HR information.

## 14.2 Functional Requirements

ESS must provide:

- Employee login.
- Own profile viewing.
- Profile change requests.
- Attendance information.
- Leave applications.
- Leave status.
- Salary slips.
- PF information.
- Notifications.
- Request history.

## 14.3 Access Restrictions

- Employees can access their own records only.
- Employee Code cannot be changed.
- Salary and PF records cannot be directly edited.
- Profile changes require approval.
- ESS cannot bypass HR workflows.

## 14.4 Acceptance Criteria

- Employee login is secure.
- Employee cannot view another employee's information.
- Requests display accurate status.
- Protected fields cannot be directly changed.

---

# 15. Notifications and Announcements

## 15.1 Notification Channels

- In-app notifications.
- Email notifications.

## 15.2 Functional Requirements

The system should notify relevant users about:

- New approval requests.
- Approved requests.
- Rejected requests.
- Leave applications.
- Profile change decisions.
- Important HR workflow events.

## 15.3 HR Announcements

- HR Admin can prepare announcements.
- HR announcements require Director approval.
- Publication must follow approval.
- Announcement history must be retained.

Notifications must not expose confidential information to unauthorized users.

---

# 16. Reports and Dashboards

## 16.1 Director Dashboard

Expected information:

- Employee strength.
- Organizational summaries.
- Pending approvals.
- Management-level HR summaries.

## 16.2 HR Dashboard

Expected information:

- Employee statistics.
- Employee status summaries.
- Pending HR requests.
- Department Manager scope requests.
- HR operational summaries.

## 16.3 Department Manager Dashboard

Expected information:

- Assigned department employees.
- Pending departmental approvals.
- Permitted departmental summaries.

## 16.4 Payroll Reports

- Monthly payroll.
- Salary summaries.
- Payroll processing status.
- Historical payroll reports.

## 16.5 Attendance Reports

- Daily attendance.
- Monthly attendance.
- Employee attendance history.
- Attendance summaries.

## 16.6 PF Reports

- Employee PF balances.
- PF contributions.
- PF loans.
- PF withdrawals.
- PF profit.

All reports must respect role and scope permissions.

---

# 17. Audit and Compliance

The system must maintain audit history for sensitive operations.

Auditable events include:

- Employee creation and modification.
- Employee status changes.
- Organization changes.
- Assignment history.
- Role changes.
- Approval and rejection.
- Payroll processing.
- PF transactions.
- Data imports.
- Session termination.
- Backup operations.

Audit information must identify the action, responsible user and relevant record.

Historical audit information must not be silently deleted.

---

# 18. Backup and Recovery

The system must support:

- Daily server-side database backups.
- 30-day backup retention.
- Restricted backup access.
- Backup history.
- Database restoration.
- Recovery verification.

Backup and restore operations must be tested before production use.

---

# 19. Non-Functional Requirements

## 19.1 Security

- Secure authentication.
- Email OTP two-factor authentication.
- Role-based authorization.
- Scope-based authorization.
- Secure password hashing.
- Encrypted sensitive credentials.
- Audit logging.

## 19.2 Data Integrity

- Unique Employee Codes.
- Foreign key constraints.
- Valid organization relationships.
- Transaction-safe operations.
- No silent overwrites.
- Historical data preservation.
- Concurrency-safe code generation.

## 19.3 Reliability

- Database transactions for multi-record operations.
- Controlled error handling.
- Data validation before persistence.
- Safe migration procedures.
- Backup and recovery capability.

## 19.4 Maintainability

- Modular backend structure.
- Reusable business services.
- Separate schemas and database models.
- Version-controlled migrations.
- Documented business rules.
- Automated tests.

## 19.5 Usability

- Clear navigation.
- Consistent interface.
- Search and filtering.
- Useful validation messages.
- Responsive frontend.
- English and Urdu language support.

## 19.6 Hosting

- Local hosting.
- Centralized PostgreSQL database.
- Controlled server access.
- Separate development and test environments.

---

# 20. Technology Requirements

## 20.1 Backend

- Python 3.12.
- FastAPI.
- SQLAlchemy.
- PostgreSQL 18.
- Alembic.
- Pydantic.
- JWT.
- Argon2 password hashing.
- Pytest.
- OpenPyXL.

## 20.2 Frontend

Planned technology:

- React.
- TypeScript.
- Vite.
- Tailwind CSS.
- shadcn/ui.

## 20.3 Database

Development database:

`udl_hrms_db`

Test database:

`udl_hrms_test_db`

All schema changes must be managed through Alembic migrations.

---

# 21. Project Scope and Delivery Phases

## Phase 1 — Backend Foundation

- Project setup.
- Database configuration.
- Authentication foundation.
- Employee Master foundation.
- Organization Master.
- Assignment history.
- Initial security and approval foundation.

## Phase 2 — Employee Management

- Complete Employee Master.
- Employee profile changes.
- Employee imports.
- Historical employee data.

## Phase 3 — HR Operations

- Attendance.
- Leave.
- Approval workflows.
- Notifications.

## Phase 4 — Payroll and PF

- Salary structures.
- Payroll calculations.
- Payroll processing.
- PF contributions.
- PF loans and withdrawals.
- PF reporting.

## Phase 5 — Frontend Applications

- Admin Portal.
- ESS Portal.
- API integration.
- Role-based interfaces.

## Phase 6 — Reports and Deployment

- Dashboards.
- Management reports.
- Backup and recovery.
- Integration testing.
- Production readiness.

---

# 22. Current Implementation Status

The following are known implementation foundations as of 6 November 2026.

## Implemented Foundations

- FastAPI backend.
- PostgreSQL database connectivity.
- SQLAlchemy models.
- Alembic migrations.
- Employee Master foundation.
- Employee assignment history.
- Organization Master APIs.
- Organization automatic code generation.
- Parent-wise Department and Sub-Department code generation.
- PostgreSQL advisory-lock-based concurrency protection.
- Authentication foundation.
- Role and permission foundation.
- Department Manager scope request foundation.
- Initial audit logging foundation.
- Test database protection in relevant tests.

## Verified Test Results

Separate test runs have reported:

- Organization API tests: 40 passed.
- Backend tests excluding interactive `test_db.py`: 60 passed.
- Organization concurrency tests: 2 passed.

These results are separate runs and must not be represented as one combined test run.

## Pending Implementation

- Complete Employee Master.
- Employee Import.
- Historical data import.
- Attendance.
- Leave.
- Complete Payroll.
- Complete PF.
- EOBI and ESSI.
- Complete notifications.
- Admin Portal.
- ESS Portal.
- Reports and dashboards.
- Production backup and recovery.
- End-to-end testing.

---

# 23. Acceptance and Change Management

- A feature is complete only after implementation and testing.
- Planned features must not be described as implemented.
- Business rules must follow `Rules.md`.
- Technical architecture must follow `architect.md`.
- Development progress must be recorded in `Task.md`.
- Important decisions must be recorded in `memory.md`.
- Changes to approved business rules require authorization.
- Database changes require migration review and testing.
- Existing records and working functionality must be preserved.
- No unapproved destructive operation may be performed on the main database.

---

# 24. Related Project Documents

| Document | Purpose |
|---|---|
| PRD.md | Functional and non-functional requirements |
| Rules.md | Business rules and policies |
| architect.md | Technical architecture |
| Task.md | Development task tracker |
| memory.md | Important decisions and development history |

These documents collectively define the UDL-HRMS project baseline.

---

**End of Product Requirements Document**

---

# 18. Additional Functional Requirements Preserved from the Original SRS

This section restores functional requirements from the original UDL-HRMS SRS. These requirements remain in the product scope unless a later, explicitly approved decision changes them. A requirement marked **Pending Business Approval** must not be implemented using an invented policy.

## 18.1 Recruitment and Candidate Management

The system must support manpower requisitions and recruitment records.

- Department Manager may initiate a manpower requisition.
- HR reviews the requisition and routes it for the required authority approval.
- Director approval is required for final selection and offer issuance as specified in the original SRS, unless an authorized later policy explicitly changes this workflow.
- A requisition may contain multiple designations and multiple vacancies.
- Candidates may originate from internal referrals or external sources.
- Candidate records, interview rounds, interview feedback and selection decisions must be retained.
- Unsuccessful candidates must remain in recruitment history.
- If a selected candidate declines or does not join, the vacancy must be reopened or returned to the approved requisition process.
- Offer letters must be generated and retained with their approval and dispatch history.

## 18.2 Resignation and Withdrawal

- Employees may submit resignation requests.
- The proposed Last Working Date (LWD) must be reviewed through the configured workflow.
- The original SRS specifies HR approval of the proposed LWD.
- A resignation withdrawal request may be submitted even after resignation approval.
- Withdrawal workflow: Employee → Department Manager → HR.
- Resignation, approval, withdrawal and final status changes must be auditable.
- Effective dates must be retained; historical employment data must not be overwritten.

## 18.3 Termination and Show Cause

- Termination recommendation workflow: Department Manager → HR → Director.
- A Show Cause Notice is mandatory before a termination decision under the original SRS.
- The employee must be given 7 days to respond.
- Director makes the final decision under the original SRS.
- The decision, reason, effective date, employee response, notice and dispatch details must be retained.
- Any later policy change to this authority chain requires explicit approval and documentation.

## 18.4 Rejoining

- A rejoining employee receives a new Employee Code.
- The previous employee record and service history must remain linked.
- Verified personal details may be reused, but the new employment event must be separately recorded.
- New salary, organization assignment, attendance, leave and probation records must be established for the new employment period.
- PF treatment, including any retired-employee transfer or prior balance treatment, must follow a separately approved PF policy.

## 18.5 Attendance, Shifts and Overtime

The system must support:

- Daily attendance records and monthly attendance processing.
- Import from the existing source chain: Biometric System → Existing HRMS → Excel → UDL-HRMS.
- Direct biometric integration is not part of the initial implementation scope unless separately approved.
- Configurable shifts and rosters.
- Attendance correction requests and approval workflow: Employee → Department Manager → HR.
- Current-month correction processing; previous months are view-only after closure unless HR performs an authorized reopen with a recorded reason.
- Monthly attendance close/lock.
- Outstation attendance requests, including GPS evidence where available; HR may manually verify where GPS is unavailable.
- Overtime eligibility and calculation by employee grade/designation and approved policy.
- Executive and above are treated as flexible/no-overtime categories under the original SRS; below Executive are overtime-eligible, subject to final approved policy.
- Special Head Office peon overtime slots must be configurable.
- Head Office calendar in the original SRS: Sunday off and alternate Saturday off.
- Branch calendar in the original SRS: Saturday normally working and Sunday ordinarily off.
- Shared holiday calendar.
- Standard office timing in the original SRS: 9:00 AM–6:00 PM, with 1:00 PM–2:00 PM lunch.

The above timings and calendar patterns are baseline SRS requirements; HR must be able to configure applicable calendars and shifts. Any changed company schedule requires approval.

## 18.6 Leave Accrual, Carry-Forward and Encashment

In addition to the annual entitlements already listed, the system must support:

- Leave accrual rules.
- Monthly or annual credit methods.
- Carry-forward and expiry rules.
- Half-day leave.
- Holiday and weekly-off treatment.
- Leave encashment.
- Leave balance adjustment with reason and audit history.
- Employee leave history and balance statements.

**Pending Business Approval:** Whether Annual Leave is accrued monthly or credited in full on 1 July; carry-forward limits/expiry; encashment eligibility and calculation; probation eligibility and any other detailed leave rules.

## 18.7 Payroll Allowances, Benefits and Statutory Deductions

Payroll scope must include configurable and effective-dated salary components, including:

- Basic salary and approved allowances.
- Deductions and arrears.
- EOBI and ESSI where applicable.
- Fuel allowance.
- Eidi.
- Annual bonus.
- Overtime and other approved earnings.
- Final settlement inputs.

### Fuel Allowance

- Fuel entitlement must be maintained in litres per employee or applicable employee category.
- Fuel rate must be effective-dated.
- Temporary start, stop and change of entitlement must be supported.
- Unused litre carry-forward is **Pending Business Approval**.

### Eidi

- Eidi is a separate fixed payment twice yearly under the original SRS.
- Eligibility must consider Joining Date.
- Resigned/terminated employees who qualify under the approved policy must be considered.
- Where an eligible employee leaves before Eid, applicable Eidi must be considered in Full & Final Settlement.
- Exact eligibility cut-off and amount require approved configuration.

### Annual Bonus

- Original SRS baseline: one month of Basic Salary, prorated by complete months.
- Original SRS baseline minimum service: 3 months.
- Original SRS baseline payment timing: Ramzan.
- Eligible former employees must be considered and included in Full & Final Settlement where applicable.
- These rules must remain configurable and require policy confirmation before payroll implementation.

### Tax and Statutory Contributions

- Income tax calculation must follow the current applicable FBR rules and approved company method.
- EOBI/ESSI applicability and contribution rules must be verified against applicable statutory requirements before implementation.
- Government minimum-wage compliance must be considered.
- Employee and employer statutory shares must be separately represented where applicable.

**Pending Business Approval:** Tax calculation method, current statutory rates/thresholds, EOBI/ESSI applicability by employee category, and minimum-wage treatment.

## 18.8 Provident Fund — Additional Requirements and Clarifications

The PF module must support separate employee and employer contribution ledgers.

The original SRS describes Employee PF at 8.33% and Company PF at 8.33% of Gross Salary. It also describes partial-month calculation using Gross Salary / 30 × eligible days × 8.33% for each share.

**Pending Business Approval / Verification:**
- Confirm whether both 8.33% shares remain the approved current policy and confirm the applicable salary base.
- Confirm whether Temporary and Third Party employees are PF-ineligible, in addition to Contractual and Intern employees.
- Confirm PF membership/eligibility date and confirmation treatment.
- Confirm Zakat rate and calculation base. Do not hard-code 1.25% solely from an unverified draft.
- Confirm PF Trustee authority and exact approval chain.
- Confirm retired employee PF transfer and rejoining treatment.
- Confirm month-wise profit calculation when a PF loan is active.

The PF module must additionally support:
- Employee and employer contribution history separately.
- Combined and component-wise balances.
- Profit posting history.
- PF loan outstanding and repayment schedule.
- Loan net payable calculation after deducting prior outstanding balance.
- Normal withdrawal limit of 70% of the eligible combined employee + employer PF balance, including posted profit, subject to approved special exception.
- PF Trustee workflow and decision history.
- PF loan, PF withdrawal and Company Loan approval chains separately from ordinary department approvals.

## 18.9 Full & Final Settlement (F&F)

The system must provide a separate Full & Final Settlement workflow for employees leaving service.

It must support configurable settlement components, including as applicable:
- Final salary and unpaid salary.
- Leave encashment where approved.
- PF settlement and applicable adjustments.
- Eidi/bonus eligibility and settlement.
- Recoveries, loans and outstanding balances.
- Zakat or statutory deductions only according to approved rules.
- Settlement statement, review, approval, payment status and audit history.

The calculation formula and approval authority must be specified and approved before implementation. No settlement amount may be inferred from incomplete historical data.

## 18.10 Employee Documents and Official Letters

The system must maintain employee-related documents and official letters, including:
- Uploaded employee documents.
- Document type, issue/expiry dates where applicable.
- Access restrictions by role.
- Employment letters and other approved official letters.
- Letter templates, generated copies, approval and dispatch history.
- Document change and access audit where required.

## 18.11 ESS Additional Requirements

ESS is a separate frontend application using secured APIs; HRMS remains the authoritative employee record.

- Employees log in using Employee Code and password.
- Forgot-password flow must verify the employee through the registered email and OTP.
- Employees may view only their own authorized records.
- ESS manager approval scopes are configured independently and are not automatically inherited from HRMS Department Manager scopes.
- Only approved employee requests may synchronize changes to HRMS.
- CNIC, bank and emergency-contact changes require additional verification as configured.
- Employees may view their own finalized salary slips.
- Employees may view their own leave balance/history and permitted attendance information.
- Employees may view their own PF balances, contributions, loan and withdrawal history.
- ESS must not permit direct changes to Employee Code, salary, PF ledger or protected HR fields.

## 18.12 Notifications and Announcements

- In-app and email notifications must support request submission, assignment, approval, rejection and status changes.
- Pending approval reminders must be configurable.
- HR announcements follow: HR draft → Director approval → publication.
- Scheduled announcements must be approved before publication.
- Announcement edits and deletions after approval/publication require the configured approval process.
- Notifications must not expose confidential data to unauthorized recipients.

## 18.13 Management Dashboards and Reports

Director dashboard scope includes:
- Employee statistics.
- Joining and resignation trends.
- Leave summaries.
- Payroll summaries.
- PF summaries.
- Department and branch summaries.
- Pending approvals.

The original SRS explicitly excludes Director attendance charts. Do not add them to the Director dashboard unless approved later.

HR users require configurable reports and exports restricted to fields they are authorized to access. Department Managers see only their assigned scope.

## 18.14 Operational, Backup and Non-Functional Requirements

- HTTPS must be used in deployed environments.
- Secrets must be stored outside source code.
- Least-privilege access must be enforced.
- Audit records must retain timestamps, actor, action, old/new values and reason where applicable.
- Normal users must not edit or delete audit records.
- Daily server-side backups with 30-day retention are required.
- Super Admin may run an authorized manual server-side backup.
- Pre-update backup and post-update health checks are required for system updates.
- Restore functionality was deferred in the initial scope; recovery design and restore testing must be separately planned before production.
- The initial SRS excludes off-site backup unless later approved.
- Responsive desktop/mobile layouts, English/Urdu, LTR/RTL and light/dark themes are required.
- Exact performance/load targets remain **Pending Business Approval**.

## 18.15 Initial Out-of-Scope Items

Unless separately approved, the initial SRS excludes:
- Direct biometric device integration.
- Direct integration with the old HRMS.
- Database restore as an end-user feature (recovery remains an operational responsibility to be designed).
- Off-site backup.
- Appraisal, training and expense management.
- Multi-company support.
- Automatic account lockout solely after five failed attempts.

---

# 19. Pending Requirements Register

The following must remain open until formally approved:

1. Annual Leave accrual method and carry-forward/expiry.
2. Leave encashment formula and eligibility.
3. PF employee/employer contribution rates and salary base.
4. PF eligibility of Temporary and Third Party employees.
5. PF membership and confirmation date rules.
6. Zakat rate and calculation base.
7. Tax calculation method and current FBR values.
8. EOBI/ESSI applicability and contribution calculations.
9. Fuel entitlement carry-forward.
10. Eidi and annual bonus exact cut-offs and eligibility.
11. Overtime rates, rounding and detailed shift exceptions.
12. Exact Excel template and historical import mapping.
13. Exact historical data coverage and source mapping.
14. Notification reminder intervals.
15. PF report catalogue and PF Trustee authority details.
16. Performance and load targets.
17. Detailed Full & Final calculation and authority.
18. Any proposed change to recruitment, resignation or termination authority workflows.

A pending item is not an approved rule. Developers must not silently choose a value or workflow.

---

# 20. Requirements Traceability and Change Control

- Original SRS requirements are preserved unless a later explicit decision supersedes them.
- `Rules.md` contains approved business rules and clearly labelled pending clarifications.
- `architect.md` describes technical design, not independent policy decisions.
- `Task.md` tracks implementation and verification status.
- `memory.md` records decisions and project history.
- A requirement is not complete merely because a model or API exists; validation, authorization, workflow, audit and tests must also be verified.
