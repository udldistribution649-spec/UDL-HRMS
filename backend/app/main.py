
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.employees import router as employees_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.department_manager_scopes import (
    router as department_manager_scopes_router,
)
from app.api.v1.endpoints.organization import router as organization_router


app = FastAPI(
    title="UDL HRMS API",
    description="UDL Human Resource Management System",
    version="1.0.0",
)

app.include_router(employees_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(department_manager_scopes_router, prefix="/api/v1")
app.include_router(organization_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "application": "UDL HRMS",
        "message": "Backend is running successfully",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "UDL HRMS API",
    }
