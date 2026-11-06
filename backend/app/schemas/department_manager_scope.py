from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DepartmentManagerScopeCreate(BaseModel):
    user_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    sub_department_id: Optional[int] = Field(default=None, gt=0)
    reason: str = Field(min_length=3, max_length=500)


class DepartmentManagerScopeResponse(BaseModel):
    id: int
    user_id: int
    department_id: int
    sub_department_id: Optional[int]
    assigned_by: int
    reason: str
    is_active: bool
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentManagerScopeRevoke(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
