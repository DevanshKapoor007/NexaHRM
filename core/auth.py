"""
NexaHRM — Authentication & User Management
Dual-role auth (HR Manager / Employee), SHA-256 password hashing,
6-digit OTP email verification, HR invite code generation,
and persistent JSON-backed user store.
"""

import json
import hashlib
import os
import random
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

# ── Storage Paths ──────────────────────────────────────────────────────────────
DATA_DIR   = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
OTP_FILE   = DATA_DIR / "otp_store.json"


# ══════════════════════════════════════════════════════════════════════════════
# PASSWORD UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes password with SHA-256 + random salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return hashed, salt


def generate_hr_code(company_name: str) -> str:
    """Generates a unique HR invite code e.g. HR-4821-NEXO."""
    tag = "".join(c.upper() for c in company_name if c.isalnum())[:4] or "CORP"
    return f"HR-{random.randint(1000, 9999)}-{tag}"


# ══════════════════════════════════════════════════════════════════════════════
# USER STORE
# ══════════════════════════════════════════════════════════════════════════════

def _bootstrap_users():
    """Creates default demo HR + Employee accounts on first run."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing: Dict[str, dict] = {}

    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    if "hr@nexahrm.ai" not in existing:
        hr_hash, hr_salt   = _hash_password("HR@123")
        emp_hash, emp_salt = _hash_password("Emp@123")

        existing["hr@nexahrm.ai"] = {
            "name": "Priya Sharma",
            "email": "hr@nexahrm.ai",
            "password_hash": hr_hash,
            "salt": hr_salt,
            "role": "hr",
            "company": "NexaCorp Global",
            "hr_code": "HR-9100-NEXA",
            "is_verified": True,
            "is_onboarded": True,
        }
        existing["alex@nexahrm.ai"] = {
            "name": "Alex Mercer",
            "email": "alex@nexahrm.ai",
            "password_hash": emp_hash,
            "salt": emp_salt,
            "role": "employee",
            "company": "NexaCorp Global",
            "hr_code": "HR-9100-NEXA",
            "assigned_hr": "hr@nexahrm.ai",
            "branch": "Mumbai HQ (India)",
            "department": "Sales",
            "job_role": "Sales Representatives",
            "target_role": "Sales Managers",
            "experience_years": 4,
            "skills": ["Strategic Negotiation", "Client Relationship Management", "Salesforce CRM"],
            "kpi_score": 88.5,
            "attendance": 96.0,
            "task_completion": 92.0,
            "peer_rating": 4.6,
            "is_verified": True,
            "is_onboarded": True,
            "assigned_courses": [
                {
                    "title": "Strategic Leadership and Management Specialization",
                    "provider": "Coursera (University of Illinois)",
                    "rating": 4.8,
                    "duration_hours": 32,
                    "level": "Intermediate",
                    "url": "https://www.coursera.org/specializations/strategic-leadership",
                    "cost": "$49/mo",
                }
            ],
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)


def get_all_users() -> Dict[str, dict]:
    """Returns all registered users."""
    _bootstrap_users()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users: Dict[str, dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# OTP VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def _get_otps() -> Dict[str, dict]:
    if not OTP_FILE.exists():
        return {}
    try:
        with open(OTP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_otps(otps: Dict[str, dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OTP_FILE, "w", encoding="utf-8") as f:
        json.dump(otps, f, indent=2)


def generate_and_send_otp(email: str) -> str:
    """Generates a 6-digit OTP valid for 10 minutes."""
    otps = _get_otps()
    email_key = email.strip().lower()
    code = str(random.randint(100000, 999999))
    otps[email_key] = {"otp": code, "expires_at": time.time() + 600}
    _save_otps(otps)
    print(f"\n[NexaHRM OTP] Verification code for {email_key}: >>> {code} <<<\n")
    return code


def verify_otp_code(email: str, entered: str) -> Tuple[bool, str]:
    """Validates OTP code. Dev bypass: 123456."""
    otps = _get_otps()
    key = email.strip().lower()

    if key not in otps:
        if entered.strip() == "123456":
            _mark_verified(key)
            return True, "Email verified successfully!"
        return False, "No active OTP found. Request a new code."

    rec = otps[key]
    if time.time() > rec["expires_at"]:
        return False, "OTP expired. Please request a new code."

    if rec["otp"] == entered.strip() or entered.strip() == "123456":
        del otps[key]
        _save_otps(otps)
        _mark_verified(key)
        return True, "Email verified successfully!"

    return False, "Incorrect code. Please check your email."


def _mark_verified(email: str):
    users = get_all_users()
    if email in users:
        users[email]["is_verified"] = True
        _save_users(users)


# ══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION & REGISTRATION
# ══════════════════════════════════════════════════════════════════════════════

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Validates credentials; returns user dict (without secrets) or None."""
    users = get_all_users()
    key = email.strip().lower()
    if key in users:
        u = users[key]
        test_hash, _ = _hash_password(password, u["salt"])
        if test_hash == u["password_hash"]:
            return {k: v for k, v in u.items() if k not in ("password_hash", "salt")}
    return None


def register_hr_user(
    name: str, email: str, password: str, company: str
) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Registers a new HR Manager; generates HR code and sends OTP."""
    users = get_all_users()
    key = email.strip().lower()

    if not key or "@" not in key:
        return False, "Please provide a valid work email.", None, None
    if len(password) < 6:
        return False, "Password must be at least 6 characters.", None, None
    if key in users:
        return False, "An account with this email already exists.", None, None

    hr_code = generate_hr_code(company)
    used_codes = {u.get("hr_code") for u in users.values() if u.get("role") == "hr"}
    while hr_code in used_codes:
        hr_code = generate_hr_code(company)

    pwd_hash, salt = _hash_password(password)
    users[key] = {
        "name": name.strip(),
        "email": key,
        "password_hash": pwd_hash,
        "salt": salt,
        "role": "hr",
        "company": company.strip(),
        "hr_code": hr_code,
        "is_verified": False,
        "is_onboarded": True,
    }
    _save_users(users)
    otp = generate_and_send_otp(key)
    return True, "HR account created! Verify your email.", hr_code, otp


def validate_hr_code(hr_code: str) -> Tuple[bool, Optional[dict]]:
    """Checks if an HR code belongs to a registered HR manager."""
    users = get_all_users()
    code = hr_code.strip().upper()
    for u in users.values():
        if u.get("role") == "hr" and u.get("hr_code", "").upper() == code:
            return True, u
    return False, None


def register_employee_user(
    name: str,
    email: str,
    password: str,
    hr_code: str,
    department: str = "General",
    job_role: str = "Associate",
    target_role: str = "Senior Associate",
) -> Tuple[bool, str, Optional[str]]:
    """Registers an Employee linked to an HR manager via invite code."""
    users = get_all_users()
    key = email.strip().lower()

    if not key or "@" not in key:
        return False, "Please provide a valid work email.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters.", None
    if key in users:
        return False, "An account with this email already exists.", None

    valid, hr_data = validate_hr_code(hr_code)
    if not valid or not hr_data:
        return False, f"Invalid HR Code '{hr_code}'. Obtain a valid code from your HR department.", None

    pwd_hash, salt = _hash_password(password)
    users[key] = {
        "name": name.strip(),
        "email": key,
        "password_hash": pwd_hash,
        "salt": salt,
        "role": "employee",
        "company": hr_data.get("company", "Enterprise"),
        "hr_code": hr_data.get("hr_code"),
        "assigned_hr": hr_data.get("email"),
        "department": department,
        "job_role": job_role,
        "target_role": target_role,
        "is_verified": False,
        "is_onboarded": False,
    }
    _save_users(users)
    otp = generate_and_send_otp(key)
    return (
        True,
        f"Account registered and linked to {hr_data['name']} ({hr_data['company']})! Verify your email.",
        otp,
    )


def complete_employee_onboarding(
    email: str,
    branch: str,
    department: str,
    job_role: str,
    target_role: str,
    experience_years: int,
    skills: List[str],
    assigned_courses: List[dict] = [],
    roadmap: dict = {},
) -> Tuple[bool, str]:
    """Saves full onboarding profile for a new employee."""
    users = get_all_users()
    key = email.strip().lower()
    if key not in users:
        return False, "User account not found."

    users[key].update({
        "branch": branch,
        "department": department,
        "job_role": job_role,
        "target_role": target_role,
        "experience_years": experience_years,
        "skills": skills,
        "kpi_score": round(random.uniform(82.0, 95.0), 1),
        "attendance": round(random.uniform(94.0, 99.0), 1),
        "task_completion": round(random.uniform(88.0, 98.0), 1),
        "peer_rating": round(random.uniform(4.4, 4.9), 1),
        "assigned_courses": assigned_courses,
        "roadmap": roadmap,
        "is_onboarded": True,
    })
    _save_users(users)
    return True, "Onboarding completed successfully!"


def get_employees_for_hr(hr_code: str) -> List[dict]:
    """Returns all employees linked to a given HR code."""
    users = get_all_users()
    code = hr_code.strip().upper()
    return [
        {k: v for k, v in u.items() if k not in ("password_hash", "salt")}
        for u in users.values()
        if u.get("role") == "employee" and u.get("hr_code", "").upper() == code
    ]


def assign_courses_to_employee(
    email: str, courses: List[dict], target_role: Optional[str] = None
) -> bool:
    """HR assigns custom courses or updates a target role for an employee."""
    users = get_all_users()
    key = email.strip().lower()
    if key in users:
        users[key]["assigned_courses"] = courses
        if target_role:
            users[key]["target_role"] = target_role
        _save_users(users)
        return True
    return False
