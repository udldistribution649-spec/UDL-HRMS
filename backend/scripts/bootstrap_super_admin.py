import argparse
import getpass
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.employee import Employee
from app.models.security import AuditLog, Role, User, UserRole


ROLE_NAME = "Super Admin"


def get_root_employee(db, employee_code):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .one_or_none()
    )

    if employee is None or not employee.is_active:
        raise ValueError("Root Employee Code does not exist or is inactive.")

    roots = (
        db.query(Employee)
        .filter(
            Employee.is_active.is_(True),
            Employee.reporting_manager_id.is_(None),
        )
        .all()
    )

    if len(roots) != 1 or roots[0].id != employee.id:
        raise ValueError(
            "Exactly one active root employee is required. "
            f"Found: {len(roots)}."
        )

    return employee


def get_it_employee(db, employee_code, root_employee):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .one_or_none()
    )

    if employee is None or not employee.is_active:
        raise ValueError("IT Employee Code does not exist or is inactive.")

    if employee.id == root_employee.id:
        raise ValueError(
            "IT Super Admin must be a separate employee from Root Employee."
        )

    return employee


def get_super_admin_role(db):
    roles = (
        db.query(Role)
        .filter(func.lower(Role.name) == ROLE_NAME.lower())
        .all()
    )

    if len(roles) > 1:
        raise ValueError("Multiple Super Admin roles found.")

    return roles[0] if roles else None

def apply_bootstrap_changes(
    db,
    root_employee,
    it_employee,
    username,
    password,
    role,
    user,
    user_role,
):
    if role is None:
        role = Role(
            name=ROLE_NAME,
            description="System administrator account",
            is_active=True,
        )
        db.add(role)
        db.flush()
    elif not role.is_active:
        role.is_active = True

    if user is None:
        user = User(
            employee_id=it_employee.id,
            username=username,
            password_hash=hash_password(password),
            is_active=True,
            must_change_password=True,
        )
        db.add(user)
        db.flush()

    if user_role is None:
        db.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_by=None,
            )
        )

    db.flush()

    db.add(
        AuditLog(
            actor_user_id=None,
            action="SUPER_ADMIN_BOOTSTRAP",
            entity_type="User",
            entity_id=user.id,
            old_values=None,
            new_values={
                "root_employee_code": root_employee.employee_code,
                "it_employee_code": it_employee.employee_code,
                "username": user.username,
                "role": ROLE_NAME,
                "must_change_password": user.must_change_password,
            },
            reason="Initial Super Admin bootstrap",
            ip_address=None,
        )
    )

    db.commit()
    return user


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap Super Admin for an existing IT employee."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit changes. Default mode is dry-run.",
    )
    args = parser.parse_args()

    print("\nUDL HRMS - Super Admin Bootstrap")
    print("--------------------------------")

    root_code = input("Existing Root Employee Code: ").strip()
    it_code = input("Existing IT Employee Code: ").strip()
    username = input("Super Admin username: ").strip()

    if not root_code or not it_code or not username:
        print("ERROR: All fields are required.")
        return 1

    password = None

    try:
        with SessionLocal() as db:
            # Validate existing employee records.
            root_employee = get_root_employee(db, root_code)
            it_employee = get_it_employee(db, it_code, root_employee)
            role = get_super_admin_role(db)

            user = (
                db.query(User)
                .filter(User.employee_id == it_employee.id)
                .one_or_none()
            )

            username_user = (
                db.query(User)
                .filter(User.username == username)
                .one_or_none()
            )

            if user and user.username != username:
                raise ValueError(
                    "IT employee already has a different username."
                )

            if username_user and (
                user is None or username_user.id != user.id
            ):
                raise ValueError(
                    "Username is already linked to another employee."
                )

            if user and not user.is_active:
                raise ValueError(
                    "Existing IT user account is inactive. "
                    "No automatic reactivation will be performed."
                )

            user_role = None
            if user and role:
                user_role = (
                    db.query(UserRole)
                    .filter(
                        UserRole.user_id == user.id,
                        UserRole.role_id == role.id,
                    )
                    .one_or_none()
                )

            create_role = role is None
            create_user = user is None
            assign_role = user_role is None
            activate_role = role is not None and not role.is_active

            print("\nValidation successful.")
            print(f"Root Employee : {root_employee.employee_code} - {root_employee.name}")
            print(f"IT Employee   : {it_employee.employee_code} - {it_employee.name}")
            print(f"Username      : {username}")
            print(f"Create Role   : {create_role}")
            print(f"Create User   : {create_user}")
            print(f"Assign Role   : {assign_role}")
            print(f"Activate Role : {activate_role}")

            if not args.apply:
                print("\nDRY-RUN ONLY.")
                print("No database changes were made.")
                print("Use --apply only after reviewing the details.")
                return 0

            if not any(
                [create_role, create_user, assign_role, activate_role]
            ):
                print("\nSuper Admin is already configured.")
                print("No changes required.")
                return 0

            if create_user:
                password = getpass.getpass(
                    "\nEnter temporary Super Admin password: "
                )
                confirm = getpass.getpass("Confirm password: ")

                if password != confirm:
                    raise ValueError("Passwords do not match.")

                if len(password) < 12:
                    raise ValueError(
                        "Temporary password must be at least 12 characters."
                    )

            # All writes are committed together.
            apply_bootstrap_changes(
                db=db,
                root_employee=root_employee,
                it_employee=it_employee,
                username=username,
                password=password,
                role=role,
                user=user,
                user_role=user_role,
            )

            print("\nSUCCESS: Super Admin bootstrap completed.")
            print("Super Admin is assigned to the existing IT employee.")
            print("Password change is required at first login.")
            return 0

    except (ValueError, SQLAlchemyError) as exc:
        print(f"\nERROR: {exc}")
        print("Transaction rolled back. No partial changes committed.")
        return 1

    finally:
        password = None


if __name__ == "__main__":
    raise SystemExit(main())
