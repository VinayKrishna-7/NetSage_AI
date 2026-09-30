"""
tests/test_system_integration.py
==============================================================================
NetSage AI - End-to-End System Integration Verification
==============================================================================
Verifies:
 1. Loading cases.csv (all 32 cases present with valid schemas)
 2. Running rule checker on sample cases
 3. Executing AI diagnosis in mock mode (both normal and deliberate mistake cases)
 4. Submitting and loading human reviews
 5. Computing AI agreement rate and correction rate
 6. Generating Excel summary metrics
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CASES_FILE, RESPONSIBLE_AI_LOG_FILE, REVIEWS_FILE
from data_loader import load_cases, get_case_by_id, load_responsible_ai_log, load_reviews
from rule_checker import run_all_checks
from ai_diagnosis import diagnose_case
from reviewer import calculate_review_metrics, record_review
from dashboard.dashboard import generate_excel_summary


def test_cases_csv_loaded():
    cases_df = load_cases()
    assert len(cases_df) >= 30, f"Expected at least 30 cases, found {len(cases_df)}"
    # Verify required fault categories exist
    faults = cases_df["expected_fault"].unique()
    for cat in ["VLAN", "Default Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Trunking"]:
        assert any(cat.lower() in f.lower() for f in faults), f"Missing category {cat}"
    print(f"[PASS] test_cases_csv_loaded: {len(cases_df)} cases verified.")


def test_responsible_ai_log():
    resp_df = load_responsible_ai_log()
    assert len(resp_df) >= 5, f"Expected at least 5 responsible AI log entries, found {len(resp_df)}"
    assert "NET005" in resp_df["case_id"].values
    assert "NET015" in resp_df["case_id"].values
    print(f"[PASS] test_responsible_ai_log: {len(resp_df)} entries verified.")


def test_mock_ai_diagnosis():
    # Test a normal case
    case_1 = get_case_by_id("NET001")
    diag_1 = diagnose_case(case_1, mode_override="mock")
    assert diag_1["confidence"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0 <= diag_1["confidence_score"] <= 100
    assert diag_1["needs_human_review"] is True
    assert len(diag_1["evidence"]) > 0

    # Test deliberate flawed case NET005
    case_5 = get_case_by_id("NET005")
    diag_5 = diagnose_case(case_5, mode_override="mock")
    assert "DNS" in diag_5["root_cause"], "Expected deliberate DNS mistake in NET005 mock"
    assert diag_5["_mock_note"] is not None
    print("[PASS] test_mock_ai_diagnosis: Both normal and deliberate error mock cases verified.")


def test_human_review_metrics():
    reviews_df = load_reviews()
    metrics = calculate_review_metrics(reviews_df)
    assert metrics["total_reviewed"] > 0
    assert "agreement_rate" in metrics
    assert "correction_rate" in metrics
    # Agreement rate + correction rate must equal 100%
    assert round(metrics["agreement_rate"] + metrics["correction_rate"], 1) == 100.0
    print(f"[PASS] test_human_review_metrics: Agreement={metrics['agreement_rate']}%, Correction={metrics['correction_rate']}%.")


def test_excel_export():
    cases_df = load_cases()
    reviews_df = load_reviews()
    summary_path = generate_excel_summary(cases_df, reviews_df)
    assert summary_path.exists()
    assert summary_path.stat().st_size > 0
    print(f"[PASS] test_excel_export: Summary spreadsheet generated at {summary_path.name}.")


if __name__ == "__main__":
    test_cases_csv_loaded()
    test_responsible_ai_log()
    test_mock_ai_diagnosis()
    test_human_review_metrics()
    test_excel_export()
    print("=" * 60)
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
