"""
NexaHRM — Automated Test Suite & Validation Harness
Runs unit tests across authentication, data processing, ML inference,
recommender engines, and course matching.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


class TestNexaHRM(unittest.TestCase):

    def test_01_config_paths(self):
        """Verify core paths resolve correctly."""
        from core.config import BASE_DIR, DATA_RAW_DIR, ATTRITION_DATA_PATH
        self.assertTrue(BASE_DIR.exists())
        self.assertTrue(DATA_RAW_DIR.exists())
        self.assertTrue(ATTRITION_DATA_PATH.exists())

    def test_02_data_loaders(self):
        """Verify data loaders return valid non-empty dataframes."""
        from core.data_loader import get_attrition_df, get_performance_df, get_training_df
        df_att = get_attrition_df()
        df_perf = get_performance_df()
        df_train = get_training_df()

        self.assertGreater(len(df_att), 0)
        self.assertGreater(len(df_perf), 0)
        self.assertGreater(len(df_train), 0)
        self.assertIn("Attrition_Numeric", df_att.columns)
        self.assertIn("ProductivityIndex", df_perf.columns)

    def test_03_executive_kpis(self):
        """Verify executive KPI calculation."""
        from core.data_loader import get_executive_kpis
        kpis = get_executive_kpis()
        self.assertGreater(kpis["total_headcount"], 0)
        self.assertGreater(kpis["retention_rate"], 0)
        self.assertGreater(kpis["avg_salary"], 0)

    def test_04_auth_system(self):
        """Verify user authentication, registration, and HR code validation."""
        from core.auth import (
            authenticate_user, register_hr_user, validate_hr_code,
            register_employee_user, get_employees_for_hr
        )

        # Test Demo HR login
        hr_user = authenticate_user("hr@nexahrm.ai", "HR@123")
        self.assertIsNotNone(hr_user)
        self.assertEqual(hr_user["role"], "hr")

        # Test Demo Employee login
        emp_user = authenticate_user("alex@nexahrm.ai", "Emp@123")
        self.assertIsNotNone(emp_user)
        self.assertEqual(emp_user["role"], "employee")

        # Test HR Code Validation
        valid, data = validate_hr_code("HR-9100-NEXA")
        self.assertTrue(valid)

    def test_05_attrition_prediction(self):
        """Verify ML attrition predictor inference."""
        from core.predictor import predictor
        sample_emp = {
            "Age": 32, "Department": "Sales", "JobRole": "Sales Executive",
            "MonthlyIncome": 4500, "OverTime": "Yes", "TotalWorkingYears": 6,
            "YearsAtCompany": 3, "YearsInCurrentRole": 2, "YearsSinceLastPromotion": 3,
            "YearsWithCurrManager": 1, "EnvironmentSatisfaction": 2, "JobSatisfaction": 2,
            "RelationshipSatisfaction": 3, "WorkLifeBalance": 2, "DistanceFromHome": 15,
            "MaritalStatus": "Single", "BusinessTravel": "Travel_Rarely"
        }
        res = predictor.predict_attrition(sample_emp)
        self.assertIn("attrition_probability", res)
        self.assertIn("risk_level", res)
        self.assertIsInstance(res["attrition_probability"], float)

    def test_06_promotion_prediction(self):
        """Verify ML promotion readiness scoring."""
        from core.predictor import predictor
        sample_eval = {
            "Department": "Sales", "KPI Score": 92.0, "Task Completion (%)": 95.0,
            "Attendance (%)": 98.0, "Peer Rating": 4.8, "Manager Feedback": 4.7,
            "Work Hours Logged": 42.0
        }
        res = predictor.predict_promotion(sample_eval)
        self.assertIn("promotion_probability", res)
        self.assertIn("productivity_index", res)
        self.assertGreaterEqual(res["productivity_index"], 85.0)

    def test_07_training_outcome_prediction(self):
        """Verify ML training success prediction."""
        from core.predictor import predictor
        sample_train = {
            "DepartmentType": "Sales", "Training Cost": 1200,
            "Training Duration(Days)": 5, "Engagement Score": 4.5,
            "Satisfaction Score": 4.2, "Work-Life Balance Score": 4.0
        }
        res = predictor.predict_training_outcome(sample_train)
        self.assertIn("success_probability", res)
        self.assertGreaterEqual(res["success_probability"], 0.0)
        self.assertLessEqual(res["success_probability"], 100.0)

    def test_08_onet_recommender(self):
        """Verify O*NET occupation search and role comparison."""
        from core.recommender import recommender
        roles = recommender.search_roles("Sales", limit=5)
        self.assertGreater(len(roles), 0)

        comp = recommender.compare_roles("41-3091.00", "11-2022.00")
        self.assertIn("skill_match_pct", comp)
        self.assertIn("transition_difficulty", comp)

    def test_09_course_matcher(self):
        """Verify 30-60-90 plan generation and markdown export."""
        from core.course_matcher import course_matcher
        dummy_skills = [{"skill": "Strategic Negotiation", "importance": 4.8}]
        dummy_tools = [{"tool": "Salesforce CRM", "is_hot_tech": True}]

        plan = course_matcher.generate_30_60_90_plan("Sales Rep", "Sales Manager", dummy_skills, dummy_tools)
        self.assertEqual(len(plan["phases"]), 3)
        self.assertGreater(len(plan["recommended_courses"]), 0)

        md = course_matcher.export_plan_markdown(plan)
        self.assertIn("Executive Career Development Plan", md)

    def test_10_fastapi_endpoints(self):
        """Verify FastAPI REST API routes."""
        from fastapi.testclient import TestClient
        from core.api import app

        client = TestClient(app)
        r_root = client.get("/")
        self.assertEqual(r_root.status_code, 200)

        r_kpis = client.get("/api/kpis")
        self.assertEqual(r_kpis.status_code, 200)
        self.assertIn("total_headcount", r_kpis.json())


if __name__ == "__main__":
    print("=" * 70)
    print("  NexaHRM Automated Test Harness")
    print("=" * 70)
    unittest.main(verbosity=2)
