import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.organization import (
    Division,
    Department,
    SubDepartment,
)
from app.services.organization_code_service import (
    next_organization_code,
)


def unique_suffix():
    return uuid.uuid4().hex[:12].upper()


@pytest.fixture(autouse=True)
def check_test_database():
    if settings.DB_NAME != "udl_hrms_test_db":
        pytest.fail(
            "Unsafe database selected. Use HRMS_ENV_FILE=.env.test"
        )


def test_concurrent_department_code_generation():
    suffix = unique_suffix()

    setup_db = SessionLocal()
    division = None

    try:
        division = Division(
            code=f"V{suffix}",
            name=f"Concurrency Division {suffix}",
        )
        setup_db.add(division)
        setup_db.commit()
        division_id = division.id

        def create_department(index):
            db = SessionLocal()

            try:
                with db.begin():
                    code = next_organization_code(
                        db=db,
                        resource="departments",
                        parent_id=division_id,
                    )

                    db.add(
                        Department(
                            division_id=division_id,
                            code=code,
                            name=f"Concurrent Department {index} {suffix}",
                        )
                    )

                    db.flush()
                    return code
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            codes = list(
                executor.map(create_department, range(10))
            )

        assert len(codes) == 10
        assert len(set(codes)) == 10

        assert sorted(codes) == [
            f"DEP-{number:04d}"
            for number in range(1, 11)
        ]

    finally:
        if division is not None:
            cleanup_db = SessionLocal()
            try:
                cleanup_db.query(Department).filter(
                    Department.division_id == division.id
                ).delete(synchronize_session=False)

                cleanup_db.query(Division).filter(
                    Division.id == division.id
                ).delete(synchronize_session=False)

                cleanup_db.commit()
            finally:
                cleanup_db.close()

        setup_db.close()


def test_concurrent_sub_department_code_generation():
    suffix = unique_suffix()

    setup_db = SessionLocal()
    division = None

    try:
        division = Division(
            code=f"V{suffix}",
            name=f"Concurrency Division {suffix}",
        )
        setup_db.add(division)
        setup_db.flush()

        department = Department(
            division_id=division.id,
            code=f"D{suffix}",
            name=f"Concurrency Department {suffix}",
        )
        setup_db.add(department)
        setup_db.commit()

        department_id = department.id
        division_id = division.id

        def create_sub_department(index):
            db = SessionLocal()

            try:
                with db.begin():
                    code = next_organization_code(
                        db=db,
                        resource="sub-departments",
                        parent_id=department_id,
                    )

                    db.add(
                        SubDepartment(
                            department_id=department_id,
                            code=code,
                            name=f"Concurrent Sub Department {index} {suffix}",
                        )
                    )

                    db.flush()
                    return code
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=10) as executor:
            codes = list(
                executor.map(create_sub_department, range(10))
            )

        assert len(codes) == 10
        assert len(set(codes)) == 10

        assert sorted(codes) == [
            f"SUB-{number:04d}"
            for number in range(1, 11)
        ]

    finally:
        if division is not None:
            cleanup_db = SessionLocal()
            try:
                cleanup_db.query(SubDepartment).filter(
                    SubDepartment.department_id.in_(
                        cleanup_db.query(Department.id).filter(
                            Department.division_id == division_id
                        )
                    )
                ).delete(synchronize_session=False)

                cleanup_db.query(Department).filter(
                    Department.division_id == division_id
                ).delete(synchronize_session=False)

                cleanup_db.query(Division).filter(
                    Division.id == division_id
                ).delete(synchronize_session=False)

                cleanup_db.commit()
            finally:
                cleanup_db.close()

        setup_db.close()