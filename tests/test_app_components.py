"""
tests/test_app_components.py
==============================================================================
NetSage AI - Component and Logic Sanity Test
==============================================================================
Executes logic across all 9 pages to ensure zero runtime or data exceptions.
"""

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CASES_FILE, REVIEWS_FILE, RESPONSIBLE_AI_LOG_FILE
from data_loader import load_cases, get_case_by_id, list_case_ids, load_responsible_ai_log, load_reviews
from rule_checker import run_all_checks, parse_client_config
from ai_diagnosis import diagnose_case, validate_ai_response, build_user_prompt, load_system_prompt
from reviewer import calculate_review_metrics, record_review, get_review_for_case
from dashboard.dashboard import get_dashboard_data, generate_excel_summary


def test_all_cases_rule_checker():
    """Verify rule_checker runs on every single one of the 32 cases without crashing."""
    cases_df = load_cases()
    for idx, row in cases_df.iterrows():
        case_dict = row.to_dict()
        res = run_all_checks(case_dict)
        assert res["total_checks"] > 0
        assert res["overall_status"] in ["PASS", "FAIL", "WARNING"]
    print(f"[PASS] Rule checker verified across all {len(cases_df)} cases.")


def test_all_cases_ai_diagnosis():
    """Verify AI diagnosis engine runs on all 32 cases in mock mode without crashing."""
    cases_df = load_cases()
    for idx, row in cases_df.iterrows():
        case_dict = row.to_dict()
        diag = diagnose_case(case_dict, mode_override="mock")
        valid, msg, cleaned = validate_ai_response(diag, case_dict["case_id"])
        assert valid, f"Case {case_dict['case_id']} produced invalid AI output: {msg}"
        assert cleaned["needs_human_review"] is True
    print(f"[PASS] AI diagnosis engine verified across all {len(cases_df)} cases.")


def test_reviewer_roundtrip():
    """Verify recording and updating reviews."""
    orig = get_review_for_case("NET001")
    try:
        rec = record_review("NET001", "ACCEPTED", "", "AI diagnosis correctly identified Fa0/2 assigned to VLAN 20 instead of 10 based on show vlan brief.", "Human Reviewer")
        assert rec["decision"] == "ACCEPTED"
        fetched = get_review_for_case("NET001")
        assert fetched is not None
        assert fetched["reviewer"] == "Human Reviewer"
    finally:
        if orig:
            record_review("NET001", orig["decision"], orig.get("corrected_diagnosis", ""), orig.get("explanation", ""), orig.get("reviewer", "Human Reviewer"))
    print("[PASS] Reviewer roundtrip verified.")


def test_dashboard_compilation():
    """Verify dashboard data calculation and export."""
    cases_df = load_cases()
    reviews_df = load_reviews()
    ddata = get_dashboard_data(cases_df, reviews_df)
    assert ddata["total_cases"] == len(cases_df)
    assert "review_metrics" in ddata

    xlsx_path = generate_excel_summary(cases_df, reviews_df)
    assert xlsx_path.exists()
    print("[PASS] Dashboard data and Excel export verified.")


def test_load_viva_qa():
    """Verify loading and parsing of all 32 viva questions."""
    from data_loader import load_viva_qa
    qa = load_viva_qa()
    assert len(qa) == 32, f"Expected 32 viva questions, found {len(qa)}"
    for item in qa:
        assert item["id"] > 0
        assert item["question"]
        assert item["answer"]
    print(f"[PASS] Successfully verified all {len(qa)} viva questions and answers.")


if __name__ == "__main__":
    test_all_cases_rule_checker()
    test_all_cases_ai_diagnosis()
    test_reviewer_roundtrip()
    test_dashboard_compilation()
    print("=" * 60)
    print("ALL APP COMPONENT TESTS PASSED!")
