# UDL-HRMS — Development Task Tracker

**Last Updated:** 6 November 2026

## 1. Project Foundation

- [x] Project directory structure established
- [x] Python virtual environment configured
- [x] PostgreSQL 18 configured
- [x] Development database configured
- [x] Test database configured
- [x] FastAPI application initialized
- [x] SQLAlchemy database connection configured
- [x] Alembic migrations configured
- [x] Environment-based configuration implemented

## 2. Employee Master

- [x] Employee model foundation
- [x] Employee API foundation
- [x] Employee numeric code validation
- [x] Automatic employee code generation foundation
- [x] Root employee reporting manager can be NULL
- [x] Employee assignment history model
- [x] Assignment history migration
- [x] Employee code `0` interpreted as NULL manager reference

### Pending

- [ ] Complete employee profile fields
- [ ] Employee profile update workflow
- [ ] Employee status management
- [ ] Employee rejoining workflow verification
- [ ] Employee search and filtering
- [ ] Employee import module
- [ ] Historical employee data import

## 3. Organization Master

- [x] Location model and API
- [x] Division model and API
- [x] Department model and API
- [x] Sub-Department model and API
- [x] Designation model and API
- [x] Grade Type model and API
- [x] Grade model and API
- [x] Sub-Grade model and API
- [x] Parent-level uniqueness rules
- [x] Automatic organization code generation
- [x] PostgreSQL advisory transaction locks
- [x] Department concurrent code generation test
- [x] Sub-Department concurrent code generation test
- [x] Organization API tests

## 4. Authentication and Security

- [x] Password hashing foundation
- [x] JWT authentication foundation
- [x] Authentication API foundation
- [x] Role and permission foundation
- [x] Department Manager scope request foundation
- [x] Scope approval and execution API foundation
- [x] Security-related test foundation

### Pending

- [ ] Complete email OTP two-factor authentication
- [ ] Verify 15-minute session timeout
- [ ] Complete session management
- [ ] Complete password reset workflow
- [ ] Complete mandatory password change workflow
- [ ] Verify all role-based permissions
- [ ] Complete security audit verification

## 5. Approval Workflows

- [x] Department Manager scope request foundation
- [x] Scope approval/rejection API foundation
- [x] Scope execution API foundation
- [ ] Complete configurable Director approval
- [ ] Verify no self-approval
- [ ] Complete approval history
- [ ] PF Loan approval workflow
- [ ] PF Withdrawal approval workflow
- [ ] Company Loan approval workflow

## 6. Attendance Management

- [ ] Attendance data model
- [ ] Attendance APIs
- [ ] Attendance import
- [ ] Attendance correction workflow
- [ ] Monthly attendance processing
- [ ] Attendance reports

## 7. Leave Management

- [ ] Leave types and policies
- [ ] Leave balances
- [ ] Leave application
- [ ] Leave approval workflow
- [ ] Leave adjustment
- [ ] Leave reports

## 8. Payroll Management

- [ ] Salary structure
- [ ] Salary components
- [ ] Payroll calculation engine
- [ ] Attendance-based salary calculation
- [ ] Payroll processing
- [ ] Salary slips
- [ ] Payroll approval workflow
- [ ] Historical payroll import
- [ ] Payroll reports

## 9. Provident Fund

- [ ] PF eligibility rules
- [ ] PF contribution calculation
- [ ] PF balance management
- [ ] PF profit calculation
- [ ] PF loan management
- [ ] PF withdrawal management
- [ ] Zakat calculation
- [ ] PF reports

## 10. Employee Self-Service (ESS)

- [ ] ESS backend permissions
- [ ] Employee login using Employee Code
- [ ] Password reset
- [ ] Own profile viewing
- [ ] Profile change requests
- [ ] Attendance information
- [ ] Leave applications
- [ ] Salary slips
- [ ] PF information
- [ ] ESS notifications

## 11. Employee and Historical Data Import

- [ ] Excel import template
- [ ] Employee import validation
- [ ] Duplicate detection
- [ ] Organization reference validation
- [ ] Reporting manager validation
- [ ] Import preview
- [ ] Atomic import
- [ ] Import audit history
- [ ] Historical attendance import
- [ ] Historical payroll import
- [ ] Historical leave import
- [ ] Historical PF import
- [ ] PostgreSQL source connection
- [ ] SQL Server source connection
- [ ] MySQL source connection
- [ ] Encrypted source credentials

## 12. Notifications and Reports

- [ ] In-app notifications
- [ ] Email notifications
- [ ] HR announcements
- [ ] Announcement approval
- [ ] Director dashboard
- [ ] HR dashboard
- [ ] Pending approvals dashboard
- [ ] Employee reports
- [ ] Attendance reports
- [ ] Payroll reports

## 13. Frontend

### Admin Portal

- [ ] React and TypeScript setup
- [ ] Vite configuration
- [ ] Tailwind CSS setup
- [ ] shadcn/ui setup
- [ ] Login interface
- [ ] Dashboard
- [ ] Employee management screens
- [ ] Organization master screens
- [ ] Approval screens
- [ ] Payroll and PF screens
- [ ] Reports screens

### ESS Portal

- [ ] Separate React application
- [ ] Employee login
- [ ] Employee dashboard
- [ ] Profile screens
- [ ] Attendance screens
- [ ] Leave screens
- [ ] Salary slip screens
- [ ] PF screens

## 14. Backup and Deployment

- [ ] Daily automated database backup
- [ ] 30-day backup retention
- [ ] Backup access restrictions
- [ ] Database restore testing
- [ ] Production configuration
- [ ] Deployment verification

## 15. Testing and Quality Assurance

- [x] Organization API tests: 40 passed
- [x] Backend tests excluding interactive `test_db.py`: 60 passed
- [x] Organization concurrency tests: 2 passed
- [ ] Full test suite review
- [ ] Authentication integration tests
- [ ] Employee workflow integration tests
- [ ] Payroll calculation tests
- [ ] PF calculation tests
- [ ] End-to-end system testing

## 16. Next Development Priorities

1. Review and finalize project documentation.
2. Complete Organization Master verification.
3. Complete Employee Master functionality.
4. Complete Employee Import module.
5. Develop Attendance Management.
6. Develop Leave Management.
7. Develop Payroll Management.
8. Develop Provident Fund Management.
9. Develop Admin Portal.
10. Develop ESS Portal.
11. Complete integration and production testing.

---

## Task Management Rules

- Mark a task complete only after implementation and verification.
- Do not mark planned functionality as implemented.
- Update this document after meaningful development milestones.
- Do not modify the main database without explicit approval.
- Run database-related tests against `udl_hrms_test_db`.
- Record important business decisions in `Rules.md`.
- Record technical architecture changes in `architect.md`.
- Preserve completed and working functionality.

**End of Task Tracker**

## 17. Original SRS Modules Restored to the Development Backlog

These items are planned/pending unless independently implemented and verified. Do not mark them complete based only on a model or placeholder API.

### Recruitment and Employee Lifecycle
- [ ] Manpower requisition workflow
- [ ] Multiple designations/vacancies per requisition
- [ ] Candidate source and candidate records
- [ ] Interview rounds and feedback
- [ ] Final selection and offer-letter approval
- [ ] Candidate decline/non-joining vacancy reopening
- [ ] Resignation request and LWD review
- [ ] Resignation withdrawal workflow
- [ ] Termination recommendation workflow
- [ ] Show Cause Notice and 7-day response tracking
- [ ] Rejoining with linked prior employment and new Employee Code

### Attendance, Shifts and Overtime
- [ ] Attendance import from approved Excel source chain
- [ ] Shift and roster configuration
- [ ] Head Office and branch calendars
- [ ] Employee attendance correction request
- [ ] Department Manager → HR correction approval
- [ ] Monthly attendance close/lock
- [ ] Authorized HR reopen with reason
- [ ] Outstation attendance request and GPS evidence
- [ ] HR manual verification fallback
- [ ] Overtime eligibility and calculation
- [ ] Special overtime slot configuration

### Leave Enhancements
- [ ] Leave accrual engine
- [ ] Half-day leave
- [ ] Carry-forward and expiry
- [ ] Leave encashment
- [ ] Holiday/weekly-off handling
- [ ] Probation eligibility policy implementation after approval

### Payroll Enhancements
- [ ] Fuel allowance in litres
- [ ] Effective-dated fuel rates
- [ ] Temporary fuel allowance start/stop/change
- [ ] Eidi twice-yearly processing
- [ ] Annual bonus processing
- [ ] Tax calculation based on approved current FBR method
- [ ] EOBI/ESSI eligibility and contributions
- [ ] Minimum-wage validation
- [ ] Employee/employer statutory share separation
- [ ] Payroll arrears and benefit history

### PF and Full & Final
- [ ] Separate Employee and Company PF ledgers
- [ ] Confirm PF rates and salary base before implementation
- [ ] Confirm Temporary/Third Party eligibility
- [ ] PF Trustee workflow
- [ ] PF loan net payable after prior outstanding balance
- [ ] Combined-balance withdrawal cap and special approval
- [ ] Retired employee PF transfer rules
- [ ] Approved Zakat calculation
- [ ] Month-wise PF profit calculation during active loan
- [ ] Full & Final Settlement module and approval workflow

### Documents, ESS and Notifications
- [ ] Employee document repository and access control
- [ ] Official letter templates and dispatch history
- [ ] ESS independent manager approval scopes
- [ ] ESS registered-email OTP password recovery
- [ ] Additional verification for CNIC/bank/emergency-contact changes
- [ ] ESS finalized salary slips and PF transaction history
- [ ] Configurable pending approval reminders
- [ ] HR announcement draft/Director approval/publication workflow
- [ ] Approval for edits/deletions of published announcements

### Reports and Operations
- [ ] Director dashboard employee/joining/resignation/leave/payroll/PF summaries
- [ ] Department and branch summaries
- [ ] Pending approval dashboard
- [ ] HR custom reports and authorized-field exports
- [ ] PF report catalogue
- [ ] Immutable audit log verification
- [ ] Pre-update backup and post-update health check
- [ ] Production recovery/restore runbook and restore testing
- [ ] Performance and load target approval

## 18. Documentation and Policy Gate

Before implementing a pending policy-dependent feature:
- [ ] Obtain authorized business approval.
- [ ] Record the approved decision in `Rules.md`.
- [ ] Update the functional requirement in `PRD.md`.
- [ ] Update architecture if the technical design changes.
- [ ] Add implementation and test tasks here.
- [ ] Do not hard-code unapproved rates, eligibility or approval chains.
