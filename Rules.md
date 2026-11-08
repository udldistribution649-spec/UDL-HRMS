# UDL-HRMS — Business Rules

**Project:** UDL Human Resource Management System
**Document:** Business Rules and Policies
**Version:** 1.0
**Last Updated:** 6 November 2026
**Status:** Approved Decisions and Pending Policy Clarifications

---

## 1. General Rules

- Employee Master is the central employee record.
- Employee Code is unique and numeric.
- Historical data must not be fabricated.
- Sensitive changes must be auditable.
- Existing records must not be silently overwritten.
- Deactivation is preferred over deletion.
- All approval actions must record the responsible user.
- Business rules must be enforced by the backend.
- Users must only access information permitted by their roles and assigned scopes.
- Historical records must remain available to authorized users.
- Changes to approved business rules must be documented.
- No unapproved business rule may be introduced into the system.

## 2. Employee Rules

### 2.1 Employee Code

- Employee Code must contain numeric characters only.
- Maximum length: 20 characters.
- Employee Code must be unique across all employees.
- New Employee Codes are generated automatically by the backend.
- Imported Employee Codes must remain unchanged.
- Rejoining employees receive a new Employee Code.
- Employee Code cannot be changed through ESS.
- Existing Employee Codes must never be silently replaced.

### 2.2 Employee Status

Employment statuses include:

- Active
- Resigned
- Terminated
- Retired

Additional display/status handling:

- Resigned employees must be preserved as inactive records.
- Historical resigned employees must not be deleted.
- The 12 previously identified resigned employee records must remain preserved.
- Retired must remain a separate employment status.
- Employee status changes must be recorded in history.
- Deactivation must not erase historical employment information.

### 2.3 Contract Types

Contract types include:

- Permanent
- Contractual
- Probation
- Intern
- Third Party
- Temporary

Contract type must be maintained in the Employee Master.

### 2.4 Joining Date

- HR Representative enters Joining Date when an employee joins.
- Joining Date is mandatory for new employee records.
- Historical imports must use verified Joining Dates.
- Missing historical Joining Dates must remain blank.
- Never fabricate, assume or automatically generate historical Joining Dates.
- Existing resigned employee records with missing Joining Dates must be preserved without backfilling dates.

### 2.5 Employee Organization Assignment

- Location and Division are mandatory.
- Department and Sub-Department must follow the configured organization hierarchy.
- Designation and Grade information must reference valid master records.
- Organization references must be validated before saving.
- Organization assignment changes must maintain history.

### 2.6 Reporting Manager

- Every employee must have a valid reporting manager except the confirmed top-level/root employee.
- The root employee may have no reporting manager.
- Reporting Manager Code `0` represents NULL/None.
- An employee cannot report to themselves.
- Reporting Manager must be an existing employee.
- Manager references must be validated during imports.
- Manager assignment changes must maintain history.
- Circular reporting relationships must not be allowed.

### 2.7 Rejoining

- A rejoining employee must receive a new Employee Code.
- Previous employment records must remain preserved.
- Previous service history must not be silently overwritten.
- Rejoining must be recorded as a new employment event.
- PF eligibility must be evaluated according to the applicable rejoining rules.

## 3. Organization Rules

### 3.1 Organization Hierarchy

The organization hierarchy is:

Location → Division → Department → Sub-Department

Additional masters:

- Designation
- Grade Type
- Grade
- Sub-Grade

### 3.2 Organization Code Rules

Organization master codes are generated automatically by the backend.

| Master | Prefix | Sequence |
|---|---|---|
| Location | LOC | Global |
| Division | DIV | Global |
| Department | DEP | Per Division |
| Sub-Department | SUB | Per Department |
| Designation | DES | Global |

Examples:

- LOC-0001
- DIV-0001
- DEP-0001
- SUB-0001
- DES-0001

Rules:

- HR Admin must not manually enter organization master codes.
- Existing organization codes must be preserved.
- Code generation must be safe under simultaneous creation requests.
- Department codes are unique within their parent Division.
- Sub-Department codes are unique within their parent Department.
- The same Department Code may exist in different Divisions.
- The same Sub-Department Code may exist in different Departments.
- Location, Division and Designation codes are globally unique.
- Grade Type, Grade and Sub-Grade currently do not have generated code fields.

### 3.3 Organization Record Management

- Referenced organization records cannot be deleted.
- Active child records must be handled before parent deactivation.
- Organization changes must preserve employee assignment history.
- Invalid parent references must be rejected.
- Parent-child relationships must be validated by the backend.

## 4. Employee Assignment History

Changes to organizational assignment must preserve history.

History should capture:

- Employee
- Previous Location
- New Location
- Previous Division
- New Division
- Previous Department
- New Department
- Previous Sub-Department
- New Sub-Department
- Previous Designation
- New Designation
- Previous Grade
- New Grade
- Previous Reporting Manager
- New Reporting Manager
- Effective Date
- Changed By
- Reason

Rules:

- Previous assignments must remain available.
- New assignments must have an effective date.
- Historical assignment records must not be silently overwritten.
- Changes must be auditable.
- Reporting Manager changes must also maintain history.

## 5. Employee Profile Change Rules

- Employees can request changes only to permitted fields.
- Old values must remain available.
- New values must be stored as requested values.
- Supporting documents may be attached.
- HR must review requests.
- Only authorized approval can update the profile.
- Rejected requests must retain rejection reason.
- Approved requests must retain approver and approval date.
- Salary, PF and organizational changes require separate workflows.
- Employee Code cannot be changed through ESS.
- All approved profile changes must be auditable.

## 6. Governance and Administrative Authority

### 6.1 Company Policy Authority

- Directors and designated policy managers define company authority policies.
- Director approval is not mandatory in every operational workflow.
- Director approval must be optional/configurable where specified by the workflow policy.
- Approval requirements must follow the configured authority policy.

### 6.2 HR Administration

- HR Admin manages operational HR activities.
- HR Admin manages operational role assignments and permissions within approved policies.
- HR Admin may initiate requests for role definitions or changes when required.
- HR Admin must not exceed configured authority.
- HR Admin actions involving sensitive records must be audited.

### 6.3 Super Admin / IT

- Super Admin represents IT Developer / IT Manager technical authority.
- Super Admin is responsible for technical administration and backend/configuration changes.
- Super Admin does not have unrestricted company policy authority.
- IT implements backend and configuration changes according to approved requirements.
- Super Admin must not bypass business approval policies.
- Authorized Super Admin can manage user sessions and server-side backups.

### 6.4 Operational Roles

Current roles include:

- Super Admin
- HR Admin
- Director
- Department Manager
- Payroll Manager

Payroll Manager is the current Finance-related operational role. Further Finance authority arrangements may be reviewed later.

## 7. Department Manager Scope Rules

- HR Admin initiates assignment, change or revocation requests.
- Director approval is optional/configurable per request.
- If required, an authorized Director approves or rejects with a reason.
- If not required, the request can proceed without Director approval.
- HR Admin cannot directly activate a scope.
- No self-approval is allowed.
- Only an authorized approved request can be executed by Super Admin / IT.
- Manager can access only assigned departments and sub-departments.
- Manager cannot access unassigned organizational scopes.
- Ordinary approvals within manager scope can be final.
- PF Loan, PF Withdrawal and Company Loan retain separate approval chains.
- Scope assignment, changes, revocation, approval and execution must be auditable.

## 8. Authentication and Security Rules

### 8.1 Authentication

- All users require email OTP two-factor authentication.
- Passwords must be securely hashed.
- JWT-based authentication is used.
- First login requires password change by default.
- Password reset must follow a secure verification process.

### 8.2 Session Management

- Session timeout: 15 minutes.
- Super Admin can view authorized user sessions.
- Super Admin can terminate sessions.
- Session termination must be recorded where applicable.

### 8.3 Authorization

- Access must follow role and scope restrictions.
- Backend must enforce all permissions.
- Frontend visibility alone is not sufficient security.
- Department Managers must remain restricted to assigned departments/sub-departments.
- Employees using ESS must only access their own permitted records.

### 8.4 Audit Logging

Sensitive actions must create audit logs.

Examples:

- Employee creation and updates.
- Employee deactivation.
- Role assignment and changes.
- Approval and rejection.
- Payroll changes.
- PF transactions.
- Organization assignment changes.
- Session termination.
- Import operations.

Audit logs must identify the responsible user and action.

HR Admin deactivation must be audited.

## 9. Attendance Rules

- Attendance is processed monthly.
- Payroll uses previous month's attendance.
- Attendance corrections must be authorized.
- Imported attendance must be validated.
- Attendance history must be retained.
- Attendance records must be linked to the correct employee.
- Attendance processing must respect employee joining and leaving dates.

Detailed attendance calculations, overtime, late arrival, early departure and shift policies require final business approval.

## 10. Leave Rules

### 10.1 Annual Leave Entitlement

| Leave Type | Annual Entitlement |
|---|---:|
| Annual Leave (AL) | 15 days |
| Sick Leave (SL) | 10 days |
| Casual Leave (CL) | 10 days |

### 10.2 Leave Processing

- Leave applications require approval.
- Leave balance must be updated through authorized transactions.
- Rejected applications do not reduce leave balance.
- Leave history must be retained.
- Leave applications must be linked to the employee.
- Leave approval must follow configured authority and scope.
- Leave balance adjustments must be auditable.

Carry-forward, encashment, probation eligibility and detailed leave calculation rules require separate approval.

## 11. Payroll Rules

### 11.1 Payroll Period

- Financial Year: July to June.
- Payroll salary month and attendance month are separate.
- Current month salary uses previous month's attendance.
- Payroll calculations must use approved salary components.

### 11.2 Salary Processing

- Payroll must retain calculation and approval history.
- Salary calculations must be reproducible from stored inputs and approved rules.
- Payroll changes must be authorized and auditable.
- Payroll must respect employee joining and leaving dates.
- No eligible salary slip is generated for new joiners, resigned or terminated employees according to applicable payroll period rules.

### 11.3 Payroll Manager

- Payroll Manager handles payroll-related operational responsibilities.
- Access must be restricted according to assigned permissions.
- Payroll authority must follow approved company policy.

Detailed tax, overtime, arrears, deductions, bonuses, increments and final settlement rules require separate approved specifications.

## 12. Provident Fund (PF) Rules

### 12.1 Eligibility

- Contractual employees are PF-ineligible.
- Intern employees are PF-ineligible.
- The original SRS also lists Temporary and Third Party employees as PF-ineligible; confirm whether this remains current policy before implementation.
- PF starts according to the approved confirmation/membership eligibility date.
- Employee and Company PF shares must be maintained separately.
- The original SRS states Employee PF 8.33% and Company PF 8.33% of Gross Salary; confirm the rates and salary base before treating them as final.
- Rejoining employees must be evaluated under applicable PF eligibility rules.
- PF records must remain linked to the correct employee.

### 12.2 PF Contribution Calculation

Employee and Company PF contributions must be recorded as separate shares.

Original SRS baseline for each share:

If confirmation occurs during the month:

Gross Salary / 30 × Eligible Work Days × 8.33%

Otherwise:

Gross Salary × 8.33%

The original SRS states 8.33% for the Employee share and 8.33% for the Company share. Confirm the rates and salary base against the current PF policy/trust deed before treating them as final or implementing production calculations.

### 12.3 PF Withdrawal

- Normal withdrawal limit: 70% of eligible combined Employee + Company PF balance, including posted profit, as described in the original SRS.
- Special approval can permit an exception.
- Eligible withdrawal must follow the applicable approval workflow.
- Zakat may apply to eligible withdrawal and Final Settlement only according to an approved rate and calculation base.
- The 1.25% value appearing in a later draft is not treated as final until verified and approved.
- Withdrawal transactions must be auditable.

### 12.4 PF Loan

- Maximum PF loan period: 48 months.
- PF loan must follow its separate approval chain.
- Loan balance and repayment history must be retained.
- PF loan transactions must be auditable.

### 12.5 PF Profit

- PF profit during an active loan follows the approved financial-year rules.
- Profit is not paid for the period affected by an active loan.
- Profit for earlier months before the financial-year impact of the loan may be considered according to the applicable calculation.
- The exact month-wise calculation and adjustment must follow the approved PF specification.

### 12.6 PF Access Restrictions

- PF information must be restricted by role.
- HR visibility is limited to PF loan information and PF balance according to assigned permissions.
- Unauthorized users must not access PF details.
- PF transactions and balance changes must be auditable.

## 13. EOBI and ESSI Rules

- EOBI and ESSI eligibility must be maintained separately.
- Registration numbers must be stored where applicable.
- Registration dates must be stored where applicable.
- Historical values must not be fabricated.
- Eligibility and registration information must be linked to the relevant employee.
- Changes must be auditable.

## 14. Employee and Historical Data Import Rules

### 14.1 Employee Import

- Preserve source Employee Codes.
- Reject duplicate Employee Codes.
- Reject existing Employee Code conflicts.
- Do not overwrite existing employees.
- Validate Location, Division, Department and Sub-Department.
- Validate Designation, Grade Type, Grade and Sub-Grade.
- Validate reporting managers.
- Resolve managers using Employee Code.
- Reporting Manager Code `0` represents NULL for the root employee.
- Missing or invalid manager references must be reported.
- Joining Date must be verified before import.
- Missing historical Joining Dates must remain blank.
- No fake Joining Dates.
- Import must be all-or-nothing.
- Corrected re-import must not silently update existing employees.
- Import actions must be auditable.

### 14.2 Historical Data

Historical imports may include:

- Employee records.
- Attendance.
- Payroll.
- Leave.
- PF.

Rules:

- Historical information must be based on verified source data.
- Missing values must not be invented.
- Original employee codes must be preserved.
- Historical transactions must remain traceable.
- Validation errors must be reported before final import.

### 14.3 External Database Import

Supported source database types planned:

- PostgreSQL
- Microsoft SQL Server
- MySQL

Rules:

- Source credentials must be encrypted.
- Source connections must use read-only permissions.
- Access must be role-restricted.
- Source data must be validated before import.
- Import must follow atomic transaction rules.
- Source connection and import activities must be auditable.

## 15. ESS Rules

- Employee login uses Employee Code and password.
- Employees can access their own records only.
- Profile changes require approval.
- Employees cannot change Employee Code.
- Employees cannot directly change salary or PF records.
- Requests must show their current status.
- Employees can access only permitted information.
- ESS must not bypass HR approval workflows.
- Profile change requests must retain their history.
- Employee access must be disabled or restricted according to employment status and approved policy.

## 16. Notifications and Announcements

- Notifications may be delivered in-app and by email.
- Important workflow events should notify relevant users.
- Approval and rejection notifications must identify the related request.
- HR announcements require Director approval.
- Announcement approval and publication must be auditable.
- Notifications must not expose confidential employee information to unauthorized users.

## 17. Reports and Dashboards

- Director and HR dashboards must follow their assigned permissions.
- Pending approvals must be visible to authorized users.
- Department Managers must see information only within their assigned scope.
- Employee reports must respect role-based access.
- Payroll and PF reports must be restricted to authorized roles.
- Reports must use accurate stored data.
- Historical reporting must preserve the relevant period and status.

## 18. Data Protection and Backup

- Do not expose sensitive records to unauthorized users.
- Do not delete historical audit information.
- Do not store plaintext passwords.
- Database backups must be server-side.
- Backup retention: 30 days.
- Backup access must be restricted.
- Backup operations must be auditable.
- Restore procedures must be tested.
- Production backup and recovery must not depend on an ordinary user's local computer.

## 19. Database and Technical Safety Rules

- Development and test databases must remain separate.
- Test database: `udl_hrms_test_db`.
- Development database: `udl_hrms_db`.
- Database schema changes must use Alembic migrations.
- Migrations must be tested before applying them to the main database.
- No unapproved schema changes on the main database.
- Existing records must be preserved.
- Database operations involving multiple related changes must use transactions.
- Unique constraints and foreign keys must protect data integrity.
- Concurrency-sensitive operations must use appropriate database-level protection.
- Destructive operations require explicit approval.

## 20. Pending Business Policy Clarifications

The following details require further business approval and must not be assumed by developers:

- Detailed attendance and overtime calculations.
- Shift and late-arrival policies.
- Leave carry-forward and encashment.
- Leave eligibility during probation.
- Payroll tax and statutory deductions.
- Payroll arrears and final settlement calculations.
- Detailed PF month-wise profit calculation during active loans.
- Detailed rejoining PF treatment.
- Additional Finance authority and approval arrangements.
- Detailed EOBI and ESSI contribution calculations.

Until approved, these rules must not be implemented using invented assumptions.

## 21. Business Rule Change Management

- Business rules must be changed only after authorized approval.
- Important policy changes must be recorded in this document.
- Technical implementation must follow the approved rule.
- Changes affecting existing records must include a safe migration or correction plan.
- Historical records must not be silently modified.
- Developers must not independently change company policy.
- HR Admin must operate within approved authority.
- Super Admin / IT must implement approved technical changes.

## 22. Relationship Between Project Documents

| Document | Purpose |
|---|---|
| PRD.md | Functional requirements |
| Rules.md | Approved business rules and policies |
| architect.md | Technical architecture |
| Task.md | Development tasks and progress |
| memory.md | Important decisions and development history |

All project documents must remain consistent.

---

**End of Business Rules Document**

### Employment Status Catalogue — Confirmation Required

The current PRD lists Active, Resigned, Terminated and Retired. The original SRS also mentions On Probation, On Notice, Deceased and On Hold. These may represent a mixture of employment status and lifecycle flags. Do not silently discard them or implement them as final statuses without HR confirmation. Preserve the current four statuses as the presently documented baseline and keep the additional values in the pending decision register.

### Other PF Eligibility Categories

The original SRS lists Contractual, Intern, Temporary and Third Party as PF-ineligible. The current draft explicitly confirms only Contractual and Intern. Temporary and Third Party eligibility must be confirmed before PF eligibility logic is finalized.


---

# 23. Additional SRS Rules and Pending Policy Register

## 23.1 Recruitment and Employee Lifecycle

- Manpower requisition workflow baseline: Department Manager → HR → required authority approval.
- Requisitions may include multiple designations and vacancies.
- Candidate sources include internal referrals and external applicants.
- Candidate interview rounds, feedback and outcomes must be retained.
- Final selection and offer-letter approval follow the original SRS Director approval requirement unless explicitly changed by authorized policy.
- Unsuccessful candidate history must be preserved.
- Declined/non-joining candidates must not permanently consume the vacancy; return the vacancy to the approved requisition process.
- Resignation LWD approval baseline: HR review/approval.
- Resignation withdrawal baseline: Employee → Department Manager → HR, including after resignation approval.
- Termination baseline: Department Manager recommendation → HR → Director; Show Cause Notice; 7 days for employee response; Director final decision. Any change requires explicit approval.
- Rejoining creates a new employment event and new Employee Code; previous service history remains linked.

## 23.2 Attendance and Work Calendar

- Initial attendance source chain: Biometric → Existing HRMS → Excel → UDL-HRMS. Direct biometric/old HRMS integration is initially out of scope.
- Attendance correction baseline: Employee → Department Manager → HR.
- Current-month corrections are supported; closed previous months are view-only unless HR reopens with a reason.
- Monthly attendance close/lock is required.
- Outstation attendance may use GPS evidence; HR manual verification is fallback.
- Shift/roster, overtime, late/early and special overtime rules require approved configuration.
- Original SRS baseline: office 9 AM–6 PM; lunch 1 PM–2 PM; Head Office Sunday off and alternate Saturday off; branches normally Saturday working and Sunday off. These are configurable schedules, not hard-coded assumptions.
- Executive and above are described as flexible/no-overtime in the original SRS; below Executive overtime-eligible, subject to approved policy.

## 23.3 Leave

- Annual entitlement baseline: AL 15, SL 10, CL 10 days.
- Half-day leave, accrual, carry-forward, expiry, holidays and encashment must be supported.
- Monthly accrual versus full credit on 1 July, carry-forward/expiry, encashment and probation eligibility remain pending.

## 23.4 Payroll Benefits

- Fuel allowance supports employee/category litres, effective-dated fuel rates and temporary start/stop/change.
- Eidi baseline: fixed payment twice yearly, eligibility based on Joining Date; eligible leavers may require F&F inclusion.
- Annual bonus original baseline: one Basic Salary, prorated by complete months, 3-month minimum service and Ramzan payment; eligible former employees may require F&F inclusion.
- These baseline items require confirmation of current policy and exact cut-offs before implementation.
- Tax must follow the current approved FBR method.
- EOBI/ESSI eligibility and rates require statutory validation.
- Employee and employer statutory shares must be separately represented where applicable.

## 23.5 PF and F&F

- PF ledgers must separately record Employee and Company contributions.
- Original SRS baseline is 8.33% for each share, subject to confirmation.
- Original SRS PF-ineligible categories include Contractual, Intern, Temporary and Third Party; Temporary/Third Party confirmation is pending.
- Loan net payable must account for prior outstanding balance.
- Normal withdrawal cap baseline is 70% of combined Employee + Company PF balance including posted profit; special approval may permit exception.
- PF Trustee workflow and retired-employee transfer must be specified.
- Zakat rate/base remains pending verification; do not hard-code a draft value.
- Full & Final Settlement is a separate module and must include approved final salary, leave encashment, PF, eligible benefits, recoveries and outstanding balances.

## 23.6 ESS and Notifications

- ESS is a separate application; HRMS is authoritative.
- ESS manager approval scopes are independent from HRMS Department Manager scopes.
- Only approved requests synchronize to HRMS.
- CNIC, bank and emergency-contact changes may require additional verification.
- ESS supports own finalized salary slips, leave history/balance, permitted attendance, PF balance/contributions/loan/withdrawal history.
- Forgot password uses registered email verification and OTP.
- In-app/email notifications cover workflow events; reminder intervals are configurable.
- HR announcements require Director approval before publication; scheduled announcements must also be approved.

## 23.7 Reports, Documents and Operations

- Employee documents and official letters must support secure storage, templates, approval and dispatch history.
- Director dashboard includes employee statistics, joining/resignation, leave, payroll, PF, department/branch summaries and pending approvals.
- Director attendance charts are excluded in the original SRS unless later approved.
- HR reports/exports must be limited to authorized fields and scopes.
- Daily server-side backup, 30-day retention and authorized manual backup are required.
- HTTPS, least privilege, secrets protection and immutable audit history are required.
- Restore as an end-user feature and off-site backup were initially out of scope; production recovery planning remains an operational prerequisite.

## 23.8 Pending Business Approvals

Do not implement assumptions for:
- PF employee/employer rate and salary base.
- Temporary/Third Party PF eligibility.
- Zakat rate/base.
- Employment status catalogue beyond currently confirmed values.
- Leave accrual/carry-forward/encashment/probation.
- Tax method and statutory rates.
- EOBI/ESSI eligibility.
- Fuel carry-forward.
- Eidi/bonus cut-offs.
- Overtime formulas and shift exceptions.
- F&F formulas and approval chain.
- PF Trustee authority and profit allocation during active loan.
- Import template/mapping and historical data coverage.
- Notification reminder intervals.
- Performance/load targets.
