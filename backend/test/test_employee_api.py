
import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine, get_db
from app.core.security import get_current_user
from app.main import app

from app.models.organization import (
    Location,
    Division,
    Department,
    Designation,
)
from app.models.employee import Employee
from app.models.security import User, Role, UserRole

from app.api.v1.endpoints import employees as employee_endpoint


def unique_code():
    return uuid.uuid4().hex[:12].upper()


@pytest.fixture
def api_client(monkeypatch):
    if settings.DB_NAME != "udl_hrms_test_db":
        pytest.fail(
            "Unsafe database selected. Use HRMS_ENV_FILE=.env.test"
        )

    connection = engine.connect()
    outer_transaction = connection.begin()

    api_db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    current_user_id = {"id": None}

    def override_get_db():
        yield api_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(id=current_user_id["id"])
    )

    monkeypatch.setattr(
        employee_endpoint,
        "log_action",
        lambda *args, **kwargs: None,
    )

    try:
        with TestClient(app) as client:
            yield client, api_db, current_user_id
    finally:
        app.dependency_overrides.clear()
        api_db.close()
        outer_transaction.rollback()
        connection.close()


def create_test_user(db: Session):
    suffix = unique_code()

    location = Location(
        code=f"L{suffix}",
        name=f"Test Location {suffix}",
    )
    division = Division(
        code=f"V{suffix}",
        name=f"Test Division {suffix}",
    )
    designation = Designation(
        code=f"G{suffix}",
        name=f"Test Designation {suffix}",
    )

    db.add_all([location, division, designation])
    db.flush()

    department = Department(
        division_id=division.id,
        code=f"D{suffix}",
        name=f"Test Department {suffix}",
    )
    db.add(department)
    db.flush()

    employee = Employee(
        employee_code=str(uuid.uuid4().int)[:15],
        name=f"Test HR User {suffix}",
        contract_type="Permanent",
        employment_status="Active",
        joining_date=date.today(),
        location_id=location.id,
        division_id=division.id,
        department_id=department.id,
        designation_id=designation.id,
    )
    db.add(employee)
    db.flush()

    user = User(
        employee_id=employee.id,
        username=f"test_hr_{suffix}",
        password_hash="test-only-hash",
    )
    db.add(user)
    db.flush()

    role = db.query(Role).filter(
        Role.name == "HR Admin"
    ).first()

    if role is None:
        role = Role(
            name="HR Admin",
            description="HR Administrator",
            is_active=True,
        )
        db.add(role)
        db.flush()
    else:
        role.is_active = True

    db.add(
        UserRole(
            user_id=user.id,
            role_id=role.id,
        )
    )
    db.flush()

    return user, location, division, department, designation


def employee_payload(location, division, department, designation, **extra):
    payload = {
        "name": f"Test Employee {unique_code()}",
        "contract_type": "Permanent",
        "employment_status": "Active",
        "joining_date": str(date.today()),
        "location_id": location.id,
        "division_id": division.id,
        "department_id": department.id,
        "designation_id": designation.id,
        "reporting_manager_id": None,
    }
    payload.update(extra)
    return payload


def prepare_test_data(db, current_user_id):
    user, location, division, department, designation = (
        create_test_user(db)
    )
    current_user_id["id"] = user.id

    return location, division, department, designation


def test_multiple_root_employees_can_be_created(api_client):
    client, db, current_user_id = api_client

    location, division, department, designation = (
        prepare_test_data(db, current_user_id)
    )

    first_response = client.post(
        "/api/v1/employees/",
        json=employee_payload(
            location, division, department, designation
        ),
    )

    assert first_response.status_code == 201, first_response.text
    assert first_response.json()["reporting_manager_id"] is None

    second_response = client.post(
        "/api/v1/employees/",
        json=employee_payload(
            location, division, department, designation
        ),
    )

    assert second_response.status_code == 201, second_response.text
    assert second_response.json()["reporting_manager_id"] is None

    assert (
        first_response.json()["employee_code"]
        != second_response.json()["employee_code"]
    )


def test_employee_can_be_created_with_valid_reporting_manager(api_client):
    client, db, current_user_id = api_client

    location, division, department, designation = (
        prepare_test_data(db, current_user_id)
    )

    manager_response = client.post(
        "/api/v1/employees/",
        json=employee_payload(
            location, division, department, designation
        ),
    )

    assert manager_response.status_code == 201, manager_response.text

    manager_id = manager_response.json()["id"]

    employee_response = client.post(
        "/api/v1/employees/",
        json=employee_payload(
            location,
            division,
            department,
            designation,
            reporting_manager_id=manager_id,
        ),
    )

    assert employee_response.status_code == 201, employee_response.text
    assert employee_response.json()["reporting_manager_id"] == manager_id


def test_employee_cannot_be_own_reporting_manager(api_client):
    client, db, current_user_id = api_client

    location, division, department, designation = (
        prepare_test_data(db, current_user_id)
    )

    response = client.post(
        "/api/v1/employees/",
        json=employee_payload(
            location, division, department, designation
        ),
    )

    assert response.status_code == 201, response.text

    employee_id = response.json()["id"]

    update_response = client.put(
        f"/api/v1/employees/{employee_id}",
        json={
            "reporting_manager_id": employee_id,
            "effective_date": str(date.today()),
            "change_reason": "Self manager validation test",
        },
    )

    assert update_response.status_code == 400
    assert (
        "own Reporting Manager"
        in update_response.json()["detail"]
    )
