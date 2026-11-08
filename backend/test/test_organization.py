
import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine, get_db
from app.main import app

from app.models.organization import (
    Location,
    Division,
    Department,
    SubDepartment,
    Designation,
    GradeType,
    Grade,
    SubGrade,
)
from app.models.employee import Employee
from app.models.security import User, Role, UserRole

from app.api.v1.endpoints import organization as organization_endpoint

# Preserve the real DB-based role lookup before test fixtures mock it.
REAL_GET_USER_ROLES = organization_endpoint.get_user_roles


# --------------------------------------------------
# Database safety and helpers
# --------------------------------------------------

def unique_code():
    return uuid.uuid4().hex[:12].upper()


@pytest.fixture
def db():
    if settings.DB_NAME != "udl_hrms_test_db":
        pytest.fail(
            "Unsafe database selected. Set HRMS_ENV_FILE=.env.test"
        )

    session = SessionLocal()

    try:
        with session.begin():
            yield session
    finally:
        session.close()


def create_division(db):
    suffix = unique_code()

    division = Division(
        code=f"D{suffix}",
        name=f"Test Division {suffix}",
    )
    db.add(division)
    db.flush()

    return division


def create_department(db, division_id, code=None):
    department = Department(
        division_id=division_id,
        code=code or unique_code(),
        name=f"Test Department {unique_code()}",
    )
    db.add(department)
    db.flush()

    return department


def create_sub_department(db, department_id):
    record = SubDepartment(
        department_id=department_id,
        code=unique_code(),
        name=f"Test Sub Department {unique_code()}",
    )
    db.add(record)
    db.flush()

    return record


def create_location(db):
    suffix = unique_code()
    record = Location(
        code=f"L{suffix}",
        name=f"Test Location {suffix}",
    )
    db.add(record)
    db.flush()
    return record


def create_designation(db):
    suffix = unique_code()
    record = Designation(
        code=f"G{suffix}",
        name=f"Test Designation {suffix}",
    )
    db.add(record)
    db.flush()
    return record


def create_grade_type(db):
    record = GradeType(
        name=f"Test Grade Type {unique_code()}",
    )
    db.add(record)
    db.flush()
    return record


def create_grade(db, grade_type_id):
    record = Grade(
        grade_type_id=grade_type_id,
        name=f"Test Grade {unique_code()}",
    )
    db.add(record)
    db.flush()
    return record


def create_sub_grade(db, grade_id):
    record = SubGrade(
        grade_id=grade_id,
        name=f"Test Sub Grade {unique_code()}",
        pf_profit_category="General",
    )
    db.add(record)
    db.flush()
    return record


def create_test_user(db, role_name=None, role_active=True):
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
        employee_code=f"9{suffix}",
        name=f"Test Employee {suffix}",
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
        username=f"test_user_{suffix}",
        password_hash="test-only-hash",
    )
    db.add(user)
    db.flush()

    role = None

    if role_name:
        role = db.query(Role).filter(
            Role.name == role_name
        ).first()

    if role is None:
        role = Role(
            name=role_name or f"Test Role {suffix}",
            description="Authorization test role",
            is_active=role_active,
        )
        db.add(role)
    else:
        role.is_active = role_active

    db.flush()

    db.add(
        UserRole(
            user_id=user.id,
            role_id=role.id,
        )
    )
    db.flush()

    return user


# --------------------------------------------------
# API fixture
# --------------------------------------------------

@pytest.fixture
def api_client(monkeypatch):
    if settings.DB_NAME != "udl_hrms_test_db":
        pytest.fail("Unsafe database selected. Use .env.test")

    connection = engine.connect()
    outer_transaction = connection.begin()

    api_db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db():
        yield api_db

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[
        organization_endpoint.get_current_user
    ] = lambda: SimpleNamespace(id=1)

    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        lambda db, user_id: {"HR Admin"},
    )
    monkeypatch.setattr(
        organization_endpoint,
        "log_action",
        lambda **kwargs: None,
    )

    try:
        with TestClient(app) as client:
            yield client, api_db
    finally:
        app.dependency_overrides.clear()
        api_db.close()
        outer_transaction.rollback()
        connection.close()


def use_real_user_role(client, user, monkeypatch):
    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        REAL_GET_USER_ROLES,
    )

    app.dependency_overrides[
        organization_endpoint.get_current_user
    ] = lambda: SimpleNamespace(id=user.id)


# --------------------------------------------------
# Department code uniqueness
# --------------------------------------------------

def test_duplicate_department_code_same_division_rejected(db):
    division = create_division(db)
    code = unique_code()

    create_department(db, division.id, code)

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            create_department(db, division.id, code)


def test_same_department_code_different_divisions_allowed(db):
    division_one = create_division(db)
    division_two = create_division(db)
    code = unique_code()

    create_department(db, division_one.id, code)
    create_department(db, division_two.id, code)


def test_duplicate_sub_department_code_same_department_rejected(db):
    division = create_division(db)
    department = create_department(db, division.id)
    code = unique_code()

    db.add(
        SubDepartment(
            department_id=department.id,
            code=code,
            name=f"Test Sub Department {unique_code()}",
        )
    )
    db.flush()

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(
                SubDepartment(
                    department_id=department.id,
                    code=code,
                    name=f"Duplicate Sub Department {unique_code()}",
                )
            )
            db.flush()


def test_same_sub_department_code_different_departments_allowed(db):
    division = create_division(db)

    department_one = create_department(db, division.id)
    department_two = create_department(db, division.id)

    code = unique_code()

    db.add_all([
        SubDepartment(
            department_id=department_one.id,
            code=code,
            name=f"Sub Department {unique_code()}",
        ),
        SubDepartment(
            department_id=department_two.id,
            code=code,
            name=f"Sub Department {unique_code()}",
        ),
    ])

    db.flush()


# --------------------------------------------------
# Department and Sub-Department API
# --------------------------------------------------

def test_department_api_generates_unique_codes_within_division(api_client):
    client, db = api_client

    division = create_division(db)

    first_response = client.post(
        "/api/v1/organization/departments/",
        json={
            "division_id": division.id,
            "name": "First Department",
        },
    )

    second_response = client.post(
        "/api/v1/organization/departments/",
        json={
            "division_id": division.id,
            "name": "Second Department",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_code = first_response.json()["code"]
    second_code = second_response.json()["code"]

    assert first_code
    assert second_code
    assert first_code != second_code


def test_sub_department_api_generates_unique_codes_within_department(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)

    first_response = client.post(
        "/api/v1/organization/sub-departments/",
        json={
            "department_id": department.id,
            "name": "First Sub Department",
        },
    )

    second_response = client.post(
        "/api/v1/organization/sub-departments/",
        json={
            "department_id": department.id,
            "name": "Second Sub Department",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_code = first_response.json()["code"]
    second_code = second_response.json()["code"]

    assert first_code
    assert second_code
    assert first_code != second_code


def test_department_create_and_list_api(api_client):
    client, db = api_client

    division = create_division(db)

    response = client.post(
        "/api/v1/organization/departments/",
        json={
            "division_id": division.id,
            "name": "New Department",
        },
    )

    assert response.status_code == 201

    generated_code = response.json()["code"]
    assert generated_code

    listing = client.get("/api/v1/organization/departments/")

    assert listing.status_code == 200
    assert any(
        item["code"] == generated_code
        for item in listing.json()
    )


def test_sub_department_create_and_list_api(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)

    response = client.post(
        "/api/v1/organization/sub-departments/",
        json={
            "department_id": department.id,
            "name": "New Sub Department",
        },
    )

    assert response.status_code == 201

    generated_code = response.json()["code"]
    assert generated_code

    listing = client.get(
        "/api/v1/organization/sub-departments/"
    )

    assert listing.status_code == 200
    assert any(
        item["code"] == generated_code
        for item in listing.json()
    )


def test_department_update_api(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)

    response = client.put(
        f"/api/v1/organization/departments/{department.id}",
        json={"name": "Updated Department"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Department"


def test_sub_department_update_api(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)
    sub_department = create_sub_department(db, department.id)

    response = client.put(
        f"/api/v1/organization/sub-departments/{sub_department.id}",
        json={"name": "Updated Sub Department"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Sub Department"


# --------------------------------------------------
# Location and Division CRUD
# --------------------------------------------------

def test_location_create_and_list_api(api_client):
    client, db = api_client

    name = f"Test Location {unique_code()}"

    response = client.post(
        "/api/v1/organization/locations/",
        json={"name": name},
    )

    assert response.status_code == 201

    generated_code = response.json()["code"]
    assert generated_code

    listing = client.get("/api/v1/organization/locations/")

    assert listing.status_code == 200
    assert any(
        item["code"] == generated_code
        for item in listing.json()
    )


def test_location_update_and_deactivate_api(api_client):
    client, db = api_client
    location = create_location(db)

    update = client.put(
        f"/api/v1/organization/locations/{location.id}",
        json={"name": f"Updated {unique_code()}"},
    )

    assert update.status_code == 200

    deactivate = client.patch(
        f"/api/v1/organization/locations/{location.id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


def test_division_create_and_list_api(api_client):
    client, db = api_client

    name = f"Test Division {unique_code()}"

    response = client.post(
        "/api/v1/organization/divisions/",
        json={"name": name},
    )

    assert response.status_code == 201

    generated_code = response.json()["code"]
    assert generated_code

    listing = client.get("/api/v1/organization/divisions/")

    assert listing.status_code == 200
    assert any(
        item["code"] == generated_code
        for item in listing.json()
    )


def test_division_update_and_deactivate_api(api_client):
    client, db = api_client
    division = create_division(db)

    update = client.put(
        f"/api/v1/organization/divisions/{division.id}",
        json={"name": f"Updated Division {unique_code()}"},
    )

    assert update.status_code == 200

    deactivate = client.patch(
        f"/api/v1/organization/divisions/{division.id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


# --------------------------------------------------
# Designation CRUD
# --------------------------------------------------

def test_designation_full_crud(api_client):
    client, db = api_client

    suffix = unique_code()
    code = f"G{suffix}"
    name = f"Designation {suffix}"

    create = client.post(
        "/api/v1/organization/designations/",
        json={"code": code, "name": name},
    )

    assert create.status_code == 201
    record_id = create.json()["id"]

    listing = client.get(
        "/api/v1/organization/designations/"
    )

    assert listing.status_code == 200
    assert any(item["id"] == record_id for item in listing.json())

    update = client.put(
        f"/api/v1/organization/designations/{record_id}",
        json={"name": f"Updated Designation {unique_code()}"},
    )

    assert update.status_code == 200

    deactivate = client.patch(
        f"/api/v1/organization/designations/{record_id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


# --------------------------------------------------
# Grade Type CRUD
# --------------------------------------------------

def test_grade_type_full_crud(api_client):
    client, db = api_client

    name = f"Grade Type {unique_code()}"

    create = client.post(
        "/api/v1/organization/grade-types/",
        json={"name": name},
    )

    assert create.status_code == 201
    record_id = create.json()["id"]

    listing = client.get(
        "/api/v1/organization/grade-types/"
    )

    assert listing.status_code == 200
    assert any(item["id"] == record_id for item in listing.json())

    update = client.put(
        f"/api/v1/organization/grade-types/{record_id}",
        json={"name": f"Updated Grade Type {unique_code()}"},
    )

    assert update.status_code == 200

    deactivate = client.patch(
        f"/api/v1/organization/grade-types/{record_id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


# --------------------------------------------------
# Grade CRUD and parent validation
# --------------------------------------------------

def test_grade_full_crud(api_client):
    client, db = api_client
    grade_type = create_grade_type(db)

    create = client.post(
        "/api/v1/organization/grades/",
        json={
            "grade_type_id": grade_type.id,
            "name": f"Grade {unique_code()}",
        },
    )

    assert create.status_code == 201
    record_id = create.json()["id"]

    listing = client.get("/api/v1/organization/grades/")

    assert listing.status_code == 200
    assert any(item["id"] == record_id for item in listing.json())

    update = client.put(
        f"/api/v1/organization/grades/{record_id}",
        json={"name": f"Updated Grade {unique_code()}"},
    )

    assert update.status_code == 200

    deactivate = client.patch(
        f"/api/v1/organization/grades/{record_id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


def test_grade_invalid_grade_type_returns_400(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/grades/",
        json={
            "grade_type_id": 999999999,
            "name": "Invalid Grade",
        },
    )

    assert response.status_code == 400


def test_inactive_grade_type_cannot_be_used_for_grade(api_client):
    client, db = api_client

    grade_type = create_grade_type(db)
    grade_type.is_active = False
    db.flush()

    response = client.post(
        "/api/v1/organization/grades/",
        json={
            "grade_type_id": grade_type.id,
            "name": "Grade Under Inactive Type",
        },
    )

    assert response.status_code == 400


# --------------------------------------------------
# Sub-Grade CRUD and parent validation
# --------------------------------------------------

def test_sub_grade_full_crud(api_client):
    client, db = api_client

    grade_type = create_grade_type(db)
    grade = create_grade(db, grade_type.id)

    create = client.post(
        "/api/v1/organization/sub-grades/",
        json={
            "grade_id": grade.id,
            "name": f"Sub Grade {unique_code()}",
            "pf_profit_category": "General",
        },
    )

    assert create.status_code == 201
    record_id = create.json()["id"]

    listing = client.get(
        "/api/v1/organization/sub-grades/"
    )

    assert listing.status_code == 200
    assert any(item["id"] == record_id for item in listing.json())

    update = client.put(
        f"/api/v1/organization/sub-grades/{record_id}",
        json={
            "name": f"Updated Sub Grade {unique_code()}",
            "pf_profit_category": "Special",
        },
    )

    assert update.status_code == 200
    assert update.json()["pf_profit_category"] == "Special"

    deactivate = client.patch(
        f"/api/v1/organization/sub-grades/{record_id}/deactivate",
        params={"reason": "Test deactivation"},
    )

    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


def test_sub_grade_invalid_grade_returns_400(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/sub-grades/",
        json={
            "grade_id": 999999999,
            "name": "Invalid Sub Grade",
        },
    )

    assert response.status_code == 400


def test_inactive_grade_cannot_be_used_for_sub_grade(api_client):
    client, db = api_client

    grade_type = create_grade_type(db)
    grade = create_grade(db, grade_type.id)
    grade.is_active = False
    db.flush()

    response = client.post(
        "/api/v1/organization/sub-grades/",
        json={
            "grade_id": grade.id,
            "name": "Sub Grade Under Inactive Grade",
        },
    )

    assert response.status_code == 400


# --------------------------------------------------
# Parent-child deactivation protection
# --------------------------------------------------

def test_parent_deactivation_blocked_by_active_children(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)
    create_sub_department(db, department.id)

    division_response = client.patch(
        f"/api/v1/organization/divisions/{division.id}/deactivate",
        params={"reason": "Testing active child protection"},
    )

    assert division_response.status_code == 409

    department_response = client.patch(
        f"/api/v1/organization/departments/{department.id}/deactivate",
        params={"reason": "Testing active child protection"},
    )

    assert department_response.status_code == 409


def test_grade_type_deactivation_blocked_by_active_grade(api_client):
    client, db = api_client

    grade_type = create_grade_type(db)
    create_grade(db, grade_type.id)

    response = client.patch(
        f"/api/v1/organization/grade-types/{grade_type.id}/deactivate",
        params={"reason": "Active grade exists"},
    )

    assert response.status_code == 409


def test_grade_deactivation_blocked_by_active_sub_grade(api_client):
    client, db = api_client

    grade_type = create_grade_type(db)
    grade = create_grade(db, grade_type.id)
    create_sub_grade(db, grade.id)

    response = client.patch(
        f"/api/v1/organization/grades/{grade.id}/deactivate",
        params={"reason": "Active sub-grade exists"},
    )

    assert response.status_code == 409


# --------------------------------------------------
# Parent validation: Department hierarchy
# --------------------------------------------------

def test_department_invalid_division_id_returns_400(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/departments/",
        json={
            "division_id": 999999999,
            "name": "Invalid Parent Department",
        },
    )

    assert response.status_code == 400


def test_sub_department_invalid_department_id_returns_400(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/sub-departments/",
        json={
            "department_id": 999999999,
            "name": "Invalid Parent Sub Department",
        },
    )

    assert response.status_code == 400


def test_department_missing_division_id_returns_422(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/departments/",
        json={
            "name": "Missing Parent Department",
        },
    )

    assert response.status_code == 422


def test_location_missing_required_name_returns_422(api_client):
    client, db = api_client

    response = client.post(
        "/api/v1/organization/locations/",
        json={},
    )

    assert response.status_code == 422


def test_inactive_division_cannot_be_used_as_department_parent(api_client):
    client, db = api_client

    division = create_division(db)
    division.is_active = False
    db.flush()

    response = client.post(
        "/api/v1/organization/departments/",
        json={
            "division_id": division.id,
            "name": "Department Under Inactive Division",
        },
    )

    assert response.status_code == 400


def test_inactive_department_cannot_be_used_as_sub_department_parent(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)
    department.is_active = False
    db.flush()

    response = client.post(
        "/api/v1/organization/sub-departments/",
        json={
            "department_id": department.id,
            "name": "Sub Department Under Inactive Department",
        },
    )

    assert response.status_code == 400


# --------------------------------------------------
# Active list filtering
# --------------------------------------------------

def test_deactivated_department_is_hidden_from_list(api_client):
    client, db = api_client

    division = create_division(db)
    department = create_department(db, division.id)

    response = client.patch(
        f"/api/v1/organization/departments/{department.id}/deactivate",
        params={"reason": "Testing inactive record visibility"},
    )

    assert response.status_code == 200

    listing = client.get(
        "/api/v1/organization/departments/"
    )

    assert listing.status_code == 200
    assert all(
        item["id"] != department.id
        for item in listing.json()
    )


# --------------------------------------------------
# Authorization tests using mocked roles
# --------------------------------------------------

def test_employee_cannot_create_organization_master(api_client, monkeypatch):
    client, db = api_client

    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        lambda db, user_id: {"Employee"},
    )

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"Unauthorized Location {unique_code()}",
        },
    )

    assert response.status_code == 403


def test_employee_cannot_update_organization_master(api_client, monkeypatch):
    client, db = api_client
    division = create_division(db)

    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        lambda db, user_id: {"Employee"},
    )

    response = client.put(
        f"/api/v1/organization/divisions/{division.id}",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 403


def test_employee_cannot_deactivate_organization_master(api_client, monkeypatch):
    client, db = api_client
    division = create_division(db)

    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        lambda db, user_id: {"Employee"},
    )

    response = client.patch(
        f"/api/v1/organization/divisions/{division.id}/deactivate",
        params={"reason": "Unauthorized attempt"},
    )

    assert response.status_code == 403


def test_super_admin_can_create_organization_master(api_client, monkeypatch):
    client, db = api_client

    monkeypatch.setattr(
        organization_endpoint,
        "get_user_roles",
        lambda db, user_id: {"Super Admin"},
    )

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"Super Admin Location {unique_code()}",
        },
    )

    assert response.status_code == 201


# --------------------------------------------------
# Authorization tests using actual database roles
# --------------------------------------------------

def test_employee_without_admin_role_cannot_create_master(
        api_client, monkeypatch
):
    client, db = api_client
    user = create_test_user(db)

    use_real_user_role(client, user, monkeypatch)

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"Unauthorized Location {unique_code()}",
        },
    )

    assert response.status_code == 403


def test_hr_admin_can_create_master_using_database_role(
        api_client, monkeypatch
):
    client, db = api_client
    user = create_test_user(db, role_name="HR Admin")

    use_real_user_role(client, user, monkeypatch)

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"HR Admin Location {unique_code()}",
        },
    )

    assert response.status_code == 201


def test_super_admin_can_create_master_using_database_role(
        api_client, monkeypatch
):
    client, db = api_client
    user = create_test_user(db, role_name="Super Admin")

    use_real_user_role(client, user, monkeypatch)

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"Super Admin Location {unique_code()}",
        },
    )

    assert response.status_code == 201


def test_inactive_hr_admin_role_cannot_create_master(
        api_client, monkeypatch
):
    client, db = api_client
    user = create_test_user(
        db,
        role_name="HR Admin",
        role_active=False,
    )

    use_real_user_role(client, user, monkeypatch)

    response = client.post(
        "/api/v1/organization/locations/",
        json={
            "name": f"Inactive Role Location {unique_code()}",
        },
    )

    assert response.status_code == 403
