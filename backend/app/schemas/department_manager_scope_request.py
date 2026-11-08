from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DepartmentManagerScopeRequestCreate(BaseModel):
    request_type: Literal["ASSIGN", "CHANGE", "REVOKE"]

    manager_user_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    sub_department_id: Optional[int] = Field(default=None, gt=0)
    existing_scope_id: Optional[int] = Field(default=None, gt=0)

    request_reason: str = Field(min_length=3, max_length=2000)

    requires_director_approval: bool = False
    director_user_id: Optional[int] = Field(default=None, gt=0)


class DepartmentManagerScopeRequestResponse(BaseModel):
    id: int
    request_type: str
    status: str

    requested_by: int
    manager_user_id: int
    department_id: int
    sub_department_id: Optional[int]
    existing_scope_id: Optional[int]

    request_reason: str

    requires_director_approval: bool
    director_user_id: Optional[int]

    approved_by: Optional[int]
    approval_reason: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]

    executed_by: Optional[int]
    executed_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentManagerScopeRequestDecision(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)
