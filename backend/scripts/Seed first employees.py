"""
UDL HRMS - One-time seed: first Root employee + IT employee.

Use ONLY when the employees table is empty and no user exists yet
(chicken-and-egg: the APIs need a login, a login needs an employee).

Run from E:\\UDL-HRMS\\backend :
    python scripts\\seed_first_employees.py            (dry-run, saves nothing)
    python scripts\\seed_first_employees.py --apply    (saves)

Enter REAL company data only. Employee assignment history is NOT created
here (it needs a user id); it starts once Super Admin exists.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.employee import Employee
from app.models.organization import (
    Department,
    Designation,
    Division,
    Location,
)


def ask(label, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def get_or_create(db, model, lookup, create_values, label):
    row = db.query(model).filter_by(**lookup).one_or_none()
    if row:
        print(f"  {label}: existing -> {row.name}")
        return row, False
    row = model(**lookup, **create_values)
    db.add(row)
    db.flush()
    print(f"  {label}: NEW -> {row.name}")
    return row, True


def ask_employee(title):
    print(f"\n--- {title} ---")
    code = ask("Employee Code (numbers only, max 20)")
    name = ask("Full name")
    contract = ask("Contract type (e.g. Permanent)", "Permanent")
    joining = ask("Joining date (YYYY-MM-DD, actual date)")
    if not code or not code.isdigit() or len(code) > 20:
        raise ValueError("Employee Code must be numeric, max 20 digits.")
    if not name or not joining:
        raise ValueError("Name and Joining date are required.")
    return code, name, contract, date.fromisoformat(joining)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    print("\nUDL HRMS - Seed first employees")
    print("-------------------------------")

    try:
        with SessionLocal() as db:
            if db.query(Employee).count() > 0:
                print("ERROR: employees table is not empty. Aborting.")
                return 1

            print("\nOrganization (shared by both employees; real values)")
            loc_code = ask("Location code")
            loc_name = ask("Location name")
            div_code = ask("Division code")
            div_name = ask("Division name")
            dep_code = ask("Department code")
            dep_name = ask("Department name")
            des_code = ask("Designation code (Root employee)")
            des_name = ask("Designation name (Root employee)")
            it_des_code = ask("Designation code (IT employee)")
            it_des_name = ask("Designation name (IT employee)")

            required = [loc_code, loc_name, div_code, div_name,
                        dep_code, dep_name, des_code, des_name,
                        it_des_code, it_des_name]
            if not all(required):
                raise ValueError("All organization fields are required.")

            root_data = ask_employee("ROOT employee (top-level, no manager)")
            it_data = ask_employee("IT employee (will become Super Admin)")
            if root_data[0] == it_data[0]:
                raise ValueError("Root and IT employee codes must differ.")

            print("\nOrganization records:")
            loc, _ = get_or_create(
                db, Location, {"code": loc_code}, {"name": loc_name}, "Location")
            div, _ = get_or_create(
                db, Division, {"code": div_code}, {"name": div_name}, "Division")
            dep, _ = get_or_create(
                db, Department,
                {"code": dep_code, "division_id": div.id},
                {"name": dep_name}, "Department")
            des_root, _ = get_or_create(
                db, Designation, {"code": des_code}, {"name": des_name},
                "Designation (root)")
            des_it, _ = get_or_create(
                db, Designation, {"code": it_des_code}, {"name": it_des_name},
                "Designation (IT)")

            def build(data, designation, manager_id):
                code, name, contract, joining = data
                return Employee(
                    employee_code=code,
                    name=name,
                    contract_type=contract,
                    employment_status="Active",
                    joining_date=joining,
                    location_id=loc.id,
                    division_id=div.id,
                    department_id=dep.id,
                    designation_id=designation.id,
                    reporting_manager_id=manager_id,
                    is_active=True,
                )

            root = build(root_data, des_root, None)
            db.add(root)
            db.flush()
            it_emp = build(it_data, des_it, root.id)
            db.add(it_emp)
            db.flush()

            print(f"\nRoot employee : {root.employee_code} - {root.name}")
            print(f"IT employee   : {it_emp.employee_code} - {it_emp.name}"
                  f" (reports to {root.employee_code})")

            if not args.apply:
                db.rollback()
                print("\nDRY-RUN ONLY. Nothing saved. Use --apply to save.")
                return 0

            db.commit()
            print("\nSUCCESS: employees created.")
            print("Next: python scripts\\bootstrap_super_admin.py --apply")
            return 0

    except (ValueError, SQLAlchemyError) as exc:
        print(f"\nERROR: {exc}")
        print("Nothing saved.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())