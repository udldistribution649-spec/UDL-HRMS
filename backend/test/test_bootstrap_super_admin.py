
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts import bootstrap_super_admin as bootstrap
from app.models.employee import Employee

def make_employee(employee_id, code, manager_id=None, active=True):
    return SimpleNamespace(
        id=employee_id,
        employee_code=code,
        name=f"Employee {code}",
        reporting_manager_id=manager_id,
        is_active=active,
    )


def test_get_root_employee_accepts_the_only_active_root():
    root = make_employee(1, "100")

    employee_query = MagicMock()
    employee_query.filter.return_value.one_or_none.return_value = root

    roots_query = MagicMock()
    roots_query.filter.return_value.all.return_value = [root]

    db = MagicMock()
    db.query.side_effect = [employee_query, roots_query]

    result = bootstrap.get_root_employee(db, "100")

    assert result is root


def test_get_root_employee_rejects_multiple_active_roots():
    root = make_employee(1, "100")
    another_root = make_employee(2, "200")

    employee_query = MagicMock()
    employee_query.filter.return_value.one_or_none.return_value = root

    roots_query = MagicMock()
    roots_query.filter.return_value.all.return_value = [
        root,
        another_root,
    ]

    db = MagicMock()
    db.query.side_effect = [employee_query, roots_query]

    with pytest.raises(ValueError, match="Exactly one active root"):
        bootstrap.get_root_employee(db, "100")


def test_get_root_employee_rejects_inactive_employee():
    root = make_employee(1, "100", active=False)

    employee_query = MagicMock()
    employee_query.filter.return_value.one_or_none.return_value = root

    db = MagicMock()
    db.query.return_value = employee_query

    with pytest.raises(ValueError, match="does not exist or is inactive"):
        bootstrap.get_root_employee(db, "100")


def test_get_it_employee_accepts_a_separate_active_employee():
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    query = MagicMock()
    query.filter.return_value.one_or_none.return_value = it_employee

    db = MagicMock()
    db.query.return_value = query

    result = bootstrap.get_it_employee(db, "200", root)

    assert result is it_employee


def test_get_it_employee_rejects_root_employee():
    root = make_employee(1, "100")

    query = MagicMock()
    query.filter.return_value.one_or_none.return_value = root

    db = MagicMock()
    db.query.return_value = query

    with pytest.raises(ValueError, match="separate employee"):
        bootstrap.get_it_employee(db, "100", root)


def test_get_it_employee_rejects_inactive_employee():
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", active=False)

    query = MagicMock()
    query.filter.return_value.one_or_none.return_value = it_employee

    db = MagicMock()
    db.query.return_value = query

    with pytest.raises(ValueError, match="does not exist or is inactive"):
        bootstrap.get_it_employee(db, "200", root)


def test_get_super_admin_role_returns_existing_role():
    role = SimpleNamespace(id=1, name="Super Admin", is_active=True)

    query = MagicMock()
    query.filter.return_value.all.return_value = [role]

    db = MagicMock()
    db.query.return_value = query

    assert bootstrap.get_super_admin_role(db) is role


def test_get_super_admin_role_returns_none_when_missing():
    query = MagicMock()
    query.filter.return_value.all.return_value = []

    db = MagicMock()
    db.query.return_value = query

    assert bootstrap.get_super_admin_role(db) is None


def test_get_super_admin_role_rejects_duplicate_roles():
    roles = [
        SimpleNamespace(id=1, name="Super Admin"),
        SimpleNamespace(id=2, name="super admin"),
    ]

    query = MagicMock()
    query.filter.return_value.all.return_value = roles

    db = MagicMock()
    db.query.return_value = query

    with pytest.raises(ValueError, match="Multiple Super Admin roles"):
        bootstrap.get_super_admin_role(db)

def test_apply_bootstrap_assigns_super_admin_to_it_employee(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    added_objects = []
    db = MagicMock()
    db.add.side_effect = added_objects.append

    monkeypatch.setattr(
        bootstrap,
        "Role",
        lambda **kwargs: SimpleNamespace(id=10, **kwargs),
    )
    monkeypatch.setattr(
        bootstrap,
        "User",
        lambda **kwargs: SimpleNamespace(id=20, **kwargs),
    )
    monkeypatch.setattr(
        bootstrap,
        "UserRole",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(
        bootstrap,
        "AuditLog",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(
        bootstrap,
        "hash_password",
        lambda password: f"hashed-{password}",
    )

    user = bootstrap.apply_bootstrap_changes(
        db=db,
        root_employee=root,
        it_employee=it_employee,
        username="it.admin",
        password="temporary-password",
        role=None,
        user=None,
        user_role=None,
    )

    assert user.employee_id == it_employee.id
    assert user.employee_id != root.id
    assert user.username == "it.admin"
    assert user.password_hash == "hashed-temporary-password"
    assert user.must_change_password is True

    created_roles = [
        obj for obj in added_objects
        if obj.name == "Super Admin"
        and hasattr(obj, "description")
    ]
    assert len(created_roles) == 1

    assigned_roles = [
        obj for obj in added_objects
        if hasattr(obj, "user_id") and hasattr(obj, "role_id")
    ]
    assert len(assigned_roles) == 1
    assert assigned_roles[0].user_id == user.id
    assert assigned_roles[0].role_id == 10

    audit_logs = [
        obj for obj in added_objects
        if getattr(obj, "action", None) == "SUPER_ADMIN_BOOTSTRAP"
    ]
    assert len(audit_logs) == 1
    assert audit_logs[0].new_values["root_employee_code"] == "100"
    assert audit_logs[0].new_values["it_employee_code"] == "200"

    # Bootstrap must never create an Employee record.
    assert not any(isinstance(obj, Employee) for obj in added_objects)

    db.commit.assert_called_once()


def test_apply_bootstrap_does_not_create_duplicate_role_or_user(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    existing_role = SimpleNamespace(
        id=10,
        name="Super Admin",
        is_active=True,
    )
    existing_user = SimpleNamespace(
        id=20,
        employee_id=it_employee.id,
        username="it.admin",
        must_change_password=True,
    )
    existing_user_role = SimpleNamespace(
        user_id=20,
        role_id=10,
    )

    added_objects = []
    db = MagicMock()
    db.add.side_effect = added_objects.append

    monkeypatch.setattr(
        bootstrap,
        "AuditLog",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    result = bootstrap.apply_bootstrap_changes(
        db=db,
        root_employee=root,
        it_employee=it_employee,
        username="it.admin",
        password=None,
        role=existing_role,
        user=existing_user,
        user_role=existing_user_role,
    )

    assert result is existing_user
    assert existing_role.is_active is True
    assert not any(hasattr(obj, "description") for obj in added_objects)
    assert not any(isinstance(obj, Employee) for obj in added_objects)
    db.commit.assert_called_once()


def test_apply_bootstrap_creates_audit_log_for_it_employee(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    role = SimpleNamespace(
        id=10,
        name="Super Admin",
        is_active=True,
    )
    user = SimpleNamespace(
        id=20,
        employee_id=it_employee.id,
        username="it.admin",
        must_change_password=True,
    )
    user_role = SimpleNamespace(user_id=20, role_id=10)

    added_objects = []
    db = MagicMock()
    db.add.side_effect = added_objects.append

    monkeypatch.setattr(
        bootstrap,
        "AuditLog",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    bootstrap.apply_bootstrap_changes(
        db=db,
        root_employee=root,
        it_employee=it_employee,
        username="it.admin",
        password=None,
        role=role,
        user=user,
        user_role=user_role,
    )

    audit = next(
        obj for obj in added_objects
        if getattr(obj, "action", None) == "SUPER_ADMIN_BOOTSTRAP"
    )

    assert audit.entity_id == user.id
    assert audit.new_values["it_employee_code"] == "200"
    assert audit.new_values["root_employee_code"] == "100"

def test_apply_bootstrap_assigns_super_admin_to_it_employee(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)
    added = []

    db = MagicMock()
    db.add.side_effect = added.append

    monkeypatch.setattr(bootstrap, "Role",
        lambda **kw: SimpleNamespace(id=10, **kw))
    monkeypatch.setattr(bootstrap, "User",
        lambda **kw: SimpleNamespace(id=20, **kw))
    monkeypatch.setattr(bootstrap, "UserRole",
        lambda **kw: SimpleNamespace(**kw))
    monkeypatch.setattr(bootstrap, "AuditLog",
        lambda **kw: SimpleNamespace(**kw))
    monkeypatch.setattr(bootstrap, "hash_password",
        lambda password: "hashed-password")

    user = bootstrap.apply_bootstrap_changes(
        db, root, it_employee, "it.admin",
        "temporary-password", None, None, None,
    )

    assert user.employee_id == it_employee.id
    assert user.employee_id != root.id
    assert user.must_change_password is True
    assert any(getattr(x, "name", None) == "Super Admin" for x in added)
    assert any(getattr(x, "action", None) == "SUPER_ADMIN_BOOTSTRAP" for x in added)
    assert not any(isinstance(x, Employee) for x in added)
    db.commit.assert_called_once()


def test_apply_bootstrap_does_not_duplicate_existing_records(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    role = SimpleNamespace(id=10, name="Super Admin", is_active=True)
    user = SimpleNamespace(
        id=20, employee_id=2, username="it.admin",
        must_change_password=True,
    )
    user_role = SimpleNamespace(user_id=20, role_id=10)

    added = []
    db = MagicMock()
    db.add.side_effect = added.append

    monkeypatch.setattr(bootstrap, "AuditLog",
        lambda **kw: SimpleNamespace(**kw))

    result = bootstrap.apply_bootstrap_changes(
        db, root, it_employee, "it.admin",
        None, role, user, user_role,
    )

    assert result is user
    assert not any(isinstance(x, Employee) for x in added)
    assert not any(getattr(x, "name", None) == "Super Admin" for x in added)
    assert not any(hasattr(x, "user_id") and hasattr(x, "role_id") for x in added)
    db.commit.assert_called_once()


def test_apply_bootstrap_audit_contains_both_employee_codes(monkeypatch):
    root = make_employee(1, "100")
    it_employee = make_employee(2, "200", manager_id=1)

    role = SimpleNamespace(id=10, name="Super Admin", is_active=True)
    user = SimpleNamespace(
        id=20, employee_id=2, username="it.admin",
        must_change_password=True,
    )
    user_role = SimpleNamespace(user_id=20, role_id=10)

    added = []
    db = MagicMock()
    db.add.side_effect = added.append

    monkeypatch.setattr(bootstrap, "AuditLog",
        lambda **kw: SimpleNamespace(**kw))

    bootstrap.apply_bootstrap_changes(
        db, root, it_employee, "it.admin",
        None, role, user, user_role,
    )

    audit = next(x for x in added if getattr(x, "action", None) == "SUPER_ADMIN_BOOTSTRAP")
    assert audit.new_values["root_employee_code"] == "100"
    assert audit.new_values["it_employee_code"] == "200"
