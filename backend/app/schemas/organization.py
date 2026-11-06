
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Location
# -------------------------

class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class LocationUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool


# -------------------------
# Division
# -------------------------

class DivisionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class DivisionUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class DivisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool


# -------------------------
# Department
# -------------------------

class DepartmentCreate(BaseModel):
    division_id: int
    name: str = Field(min_length=1, max_length=150)


class DepartmentUpdate(BaseModel):
    division_id: Optional[int] = None
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    division_id: int
    code: str
    name: str
    is_active: bool


# -------------------------
# Sub Department
# -------------------------

class SubDepartmentCreate(BaseModel):
    department_id: int
    name: str = Field(min_length=1, max_length=150)


class SubDepartmentUpdate(BaseModel):
    department_id: Optional[int] = None
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class SubDepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    code: str
    name: str
    is_active: bool


# -------------------------
# Designation
# -------------------------

class DesignationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class DesignationUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    is_active: Optional[bool] = None


class DesignationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool


# -------------------------
# Grade Type
# -------------------------

class GradeTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GradeTypeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class GradeTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool


# -------------------------
# Grade
# -------------------------

class GradeCreate(BaseModel):
    grade_type_id: int
    name: str = Field(min_length=1, max_length=100)


class GradeUpdate(BaseModel):
    grade_type_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class GradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    grade_type_id: int
    name: str
    is_active: bool


# -------------------------
# Sub Grade
# -------------------------

class SubGradeCreate(BaseModel):
    grade_id: int
    name: str = Field(min_length=1, max_length=100)
    pf_profit_category: Optional[str] = Field(default=None, max_length=30)


class SubGradeUpdate(BaseModel):
    grade_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    pf_profit_category: Optional[str] = Field(default=None, max_length=30)
    is_active: Optional[bool] = None


class SubGradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    grade_id: int
    name: str
    pf_profit_category: Optional[str] = None
    is_active: bool
