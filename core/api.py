"""
NexaHRM — Enterprise FastAPI REST API Server
Provides REST endpoints for authentication, KPI metrics, ML prediction models,
O*NET skill gap analysis, and course roadmap generation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.data_loader import get_executive_kpis
from core.predictor import predictor
from core.recommender import recommender
from core.course_matcher import course_matcher
from core.auth import (
    authenticate_user,
    register_hr_user,
    register_employee_user,
    generate_and_send_otp,
    verify_otp_code,
    get_employees_for_hr,
    get_all_users
)

app = FastAPI(
    title="NexaHRM REST API",
    description="Enterprise AI People Intelligence, Retention Prediction & Skill Navigation REST API.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────

class HRRegisterRequest(BaseModel):
    name: str
    company: str
    email: str
    password: str


class EmployeeRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    hr_code: str


class SendOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


class LoginRequest(BaseModel):
    email: str
    password: str


class CompareRolesRequest(BaseModel):
    current_soc: str
    target_soc: str


class CourseRoadmapRequest(BaseModel):
    current_role: str
    target_role: str
    missing_skills: List[Dict[str, Any]] = []
    missing_tools: List[Dict[str, Any]] = []
    provider_filter: Optional[str] = "All Providers"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def api_root():
    return {
        "status": "online",
        "app": "NexaHRM Enterprise REST API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/api/kpis")
def api_get_kpis():
    try:
        return get_executive_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/send-otp")
def api_send_otp(req: SendOTPRequest):
    otp = generate_and_send_otp(req.email)
    return {"success": True, "message": f"OTP sent to {req.email}", "otp_preview": otp}


@app.post("/api/auth/verify-otp")
def api_verify_otp(req: VerifyOTPRequest):
    ok, msg = verify_otp_code(req.email, req.otp)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    users = get_all_users()
    user = users.get(req.email.strip().lower(), {})
    user_clean = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
    return {"success": True, "message": msg, "user": user_clean}


@app.post("/api/auth/register-hr")
def api_register_hr(req: HRRegisterRequest):
    ok, msg, hr_code, otp = register_hr_user(req.name, req.email, req.password, req.company)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "hr_code": hr_code, "otp_preview": otp}


@app.post("/api/auth/register-employee")
def api_register_employee(req: EmployeeRegisterRequest):
    ok, msg, otp = register_employee_user(
        name=req.name, email=req.email, password=req.password, hr_code=req.hr_code
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "otp_preview": otp}


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"success": True, "user": user}


@app.get("/api/employees/{hr_code}")
def api_get_employees(hr_code: str):
    emps = get_employees_for_hr(hr_code)
    return {"hr_code": hr_code, "employees": emps}


@app.post("/api/predict/attrition")
def api_predict_attrition(payload: Dict[str, Any]):
    try:
        return predictor.predict_attrition(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/promotion")
def api_predict_promotion(payload: Dict[str, Any]):
    try:
        return predictor.predict_promotion(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/training")
def api_predict_training(payload: Dict[str, Any]):
    try:
        return predictor.predict_training_outcome(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/roles/search")
def api_search_roles(q: str = "Sales", limit: int = 15):
    results = recommender.search_roles(q, limit=limit)
    return {"query": q, "roles": results}


@app.post("/api/roles/compare")
def api_compare_roles(req: CompareRolesRequest):
    try:
        return recommender.compare_roles(req.current_soc, req.target_soc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/courses/roadmap")
def api_generate_roadmap(req: CourseRoadmapRequest):
    try:
        plan = course_matcher.generate_30_60_90_plan(
            req.current_role,
            req.target_role,
            req.missing_skills,
            req.missing_tools,
            provider_filter=req.provider_filter or "All Providers"
        )
        md = course_matcher.export_plan_markdown(plan)
        return {"plan": plan, "markdown": md}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
