from app.models.employee import Employee, enforce_pf_eligibility


def test_contractual_employee_pf_disabled():
    employee = Employee(
        contract_type="Contractual",
        pf_deduction_allowed=True,
    )

    enforce_pf_eligibility(None, None, employee)

    assert employee.pf_deduction_allowed is False


def test_permanent_employee_pf_unchanged():
    employee = Employee(
        contract_type="Permanent",
        pf_deduction_allowed=True,
    )

    enforce_pf_eligibility(None, None, employee)

    assert employee.pf_deduction_allowed is True

def test_contractual_pf_disabled_on_update():
    employee = Employee(
        contract_type="Permanent",
        pf_deduction_allowed=True,
    )

    employee.contract_type = "Contractual"
    enforce_pf_eligibility(None, None, employee)

    assert employee.pf_deduction_allowed is False

def test_contractual_pf_case_insensitive():
    employee = Employee(
        contract_type="  contractual  ",
        pf_deduction_allowed=True,
    )
    enforce_pf_eligibility(None, None, employee)
    assert employee.pf_deduction_allowed is False