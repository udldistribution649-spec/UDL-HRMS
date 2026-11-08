
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


EmployeeCode = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=20,
        pattern=r"^[0-9]+$",
    ),
]


class EmployeeBase(BaseModel):
    employee_code: EmployeeCode
    name: str = Field(min_length=1, max_length=150)

    contract_type: str
    employment_status: str = "Active"

    joining_date: date
    confirmation_date: Optional[date] = None

    location_id: int
    division_id: int
    department_id: int
    sub_department_id: Optional[int] = None
    designation_id: int
    grade_id: Optional[int] = None
    sub_grade_id: Optional[int] = None

    reporting_manager_id: Optional[int] = None
    previous_employee_id: Optional[int] = None

    third_party: bool = False
    third_party_company: Optional[str] = None

    pf_deduction_allowed: bool = False

    eobi_enabled: bool = False
    eobi_number: Optional[str] = None
    eobi_registration_date: Optional[date] = None

    essi_enabled: bool = False
    essi_number: Optional[str] = None
    essi_registration_date: Optional[date] = None

    zakat_exemption: bool = False
    interest_free_pf_account: bool = False


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    contract_type: str
    employment_status: str = "Active"
    joining_date: date

    location_id: int
    division_id: int
    department_id: int
    sub_department_id: Optional[int] = None
    designation_id: int
    grade_id: Optional[int] = None
    sub_grade_id: Optional[int] = None

    reporting_manager_id: int | None = None
    previous_employee_id: Optional[int] = None

    third_party: bool = False
    third_party_company: Optional[str] = None

    pf_deduction_allowed: bool = False

    eobi_enabled: bool = False
    eobi_number: Optional[str] = None
    eobi_registration_date: Optional[date] = None

    essi_enabled: bool = False
    essi_number: Optional[str] = None
    essi_registration_date: Optional[date] = None

    zakat_exemption: bool = False
    interest_free_pf_account: bool = False


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    contract_type: Optional[str] = None
    employment_status: Optional[str] = None

    confirmation_date: Optional[date] = None

    effective_date: Optional[date] = None
    change_reason: Optional[str] = Field(default=None, max_length=500)

    location_id: Optional[int] = None
    division_id: Optional[int] = None
    department_id: Optional[int] = None
    sub_department_id: Optional[int] = None
    designation_id: Optional[int] = None
    grade_id: Optional[int] = None
    sub_grade_id: Optional[int] = None

    reporting_manager_id: Optional[int] = None

    third_party: Optional[bool] = None
    third_party_company: Optional[str] = None

    pf_deduction_allowed: Optional[bool] = None

    eobi_enabled: Optional[bool] = None
    eobi_number: Optional[str] = None
    eobi_registration_date: Optional[date] = None

    essi_enabled: Optional[bool] = None
    essi_number: Optional[str] = None
    essi_registration_date: Optional[date] = None

    zakat_exemption: Optional[bool] = None
    interest_free_pf_account: Optional[bool] = None

    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeAssignmentHistoryResponse(BaseModel):
    id: int
    employee_id: int

    location_id: int
    division_id: int
    department_id: int
    sub_department_id: Optional[int] = None
    designation_id: int
    grade_id: Optional[int] = None
    sub_grade_id: Optional[int] = None

    reporting_manager_id: Optional[int] = None

    effective_from: date
    changed_by: int
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
