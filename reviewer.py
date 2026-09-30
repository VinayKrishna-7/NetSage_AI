"""
reviewer.py
==============================================================================
NetSage AI - Human Review & Oversight System
==============================================================================
Enforces human-in-the-loop governance over AI diagnoses.
Every AI diagnosis can be reviewed, verified, edited, or rejected by a network
engineer or student reviewer.

Supported Review Decisions:
 - ACCEPTED : Human engineer confirms AI diagnosis is accurate and grounded.
 - EDITED   : Human engineer corrects or refines AI diagnosis details.
 - REJECTED : Human engineer rejects AI diagnosis due to hallucination or error.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from config import (
    ALLOWED_REVIEW_DECISIONS,
    REVIEWS_FILE,
    REVIEW_STATUS_ACCEPTED,
    REVIEW_STATUS_EDITED,
    REVIEW_STATUS_REJECTED,
)

REVIEWS_COLUMNS = [
    "case_id",
    "decision",
    "corrected_diagnosis",
    "explanation",
    "reviewer",
    "timestamp",
]


def init_reviews_storage():
    """Ensure the reviews.csv file exists and is populated with baseline demo data if empty."""
    if not REVIEWS_FILE.exists() or REVIEWS_FILE.stat().st_size == 0:
        # Seed with initial reviews reflecting our baseline cases
        initial_records = [
            {
                "case_id": "NET001",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "AI diagnosis correctly identified Fa0/2 assigned to VLAN 20 instead of 10 based on show vlan brief.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 09:15:00",
            },
            {
                "case_id": "NET002",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "Confirmed VLAN 30 is missing from switch database; port reports ((Inactive)).",
                "reviewer": "Alice Chen (Student)",
                "timestamp": "2026-09-28 09:30:00",
            },
            {
                "case_id": "NET003",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "Confirmed subinterface encapsulation tag mismatch (dot1Q 12 vs 10).",
                "reviewer": "Alice Chen (Student)",
                "timestamp": "2026-09-28 09:45:00",
            },
            {
                "case_id": "NET004",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "Confirmed switchport access VLAN was mistakenly configured as Voice VLAN 150.",
                "reviewer": "Bob Patel (Student)",
                "timestamp": "2026-09-28 10:00:00",
            },
            {
                "case_id": "NET005",
                "decision": REVIEW_STATUS_EDITED,
                "corrected_diagnosis": "Client default gateway 192.168.20.1 is outside local subnet 192.168.10.0/24.",
                "explanation": "AI erroneously diagnosed DNS failure. Local gateway is outside the host subnet, preventing all off-subnet routing.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 10:20:00",
            },
            {
                "case_id": "NET008",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "Confirmed DHCP pool exhaustion; 28/28 usable leases consumed.",
                "reviewer": "Bob Patel (Student)",
                "timestamp": "2026-09-28 10:35:00",
            },
            {
                "case_id": "NET010",
                "decision": REVIEW_STATUS_EDITED,
                "corrected_diagnosis": "DHCP default-router option has typo (192.168.1.254 instead of 192.168.1.1).",
                "explanation": "AI blamed ISP outage. Running config revealed local DHCP option typo on router R1.",
                "reviewer": "Alice Chen (Student)",
                "timestamp": "2026-09-28 10:50:00",
            },
            {
                "case_id": "NET012",
                "decision": REVIEW_STATUS_ACCEPTED,
                "corrected_diagnosis": "",
                "explanation": "Confirmed client DNS server IP was mistyped as 8.8.4.40.",
                "reviewer": "Bob Patel (Student)",
                "timestamp": "2026-09-28 11:10:00",
            },
            {
                "case_id": "NET015",
                "decision": REVIEW_STATUS_EDITED,
                "corrected_diagnosis": "Missing default route on edge router R1 (Gateway of last resort is not set).",
                "explanation": "AI blamed NAT failure. In Cisco IOS, routing precedes NAT; missing default route is the primary cause.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 11:25:00",
            },
            {
                "case_id": "NET019",
                "decision": REVIEW_STATUS_REJECTED,
                "corrected_diagnosis": "Standard ACL 10 outbound drops host 192.168.10.10 via implicit deny.",
                "explanation": "AI hallucinated trunking issue. ACL counters show 87 implicit deny matches blocking host.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 11:40:00",
            },
            {
                "case_id": "NET024",
                "decision": REVIEW_STATUS_REJECTED,
                "corrected_diagnosis": "WAN interface Gi0/1 is missing 'ip nat outside' statement.",
                "explanation": "AI hallucinated physical link down condition. NAT stats report Outside interfaces: None.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 12:00:00",
            },
            {
                "case_id": "NET026",
                "decision": REVIEW_STATUS_REJECTED,
                "corrected_diagnosis": "Guest Wi-Fi subinterface Gi0/0.99 lacks an ACL restricting corporate private subnets.",
                "explanation": "AI misdiagnosed WPA2 key compromise. Default inter-VLAN routing allowed guest traffic to reach corporate VLAN.",
                "reviewer": "Prof. Miller (CCNP)",
                "timestamp": "2026-09-28 12:15:00",
            },
        ]
        df = pd.DataFrame(initial_records, columns=REVIEWS_COLUMNS)
        df.to_csv(REVIEWS_FILE, index=False, encoding="utf-8")


def load_reviews() -> pd.DataFrame:
    """Load all human reviews into a pandas DataFrame."""
    init_reviews_storage()
    try:
        df = pd.read_csv(REVIEWS_FILE, encoding="utf-8")
        return df
    except Exception:
        return pd.DataFrame(columns=REVIEWS_COLUMNS)


def get_review_for_case(case_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve the human review record for a specific case ID if present."""
    df = load_reviews()
    matches = df[df["case_id"] == case_id]
    if matches.empty:
        return None
    # Return latest review for this case
    return matches.iloc[-1].to_dict()


def record_review(
    case_id: str,
    decision: str,
    corrected_diagnosis: str = "",
    explanation: str = "",
    reviewer: str = "Anonymous Reviewer",
) -> Dict[str, Any]:
    """
    Save or update a human review decision for a case.
    Validates decision against ACCEPTED, EDITED, REJECTED.
    """
    decision_clean = decision.strip().upper()
    if decision_clean not in ALLOWED_REVIEW_DECISIONS:
        raise ValueError(
            f"Invalid review decision '{decision}'. Must be one of {ALLOWED_REVIEW_DECISIONS}"
        )

    init_reviews_storage()
    df = load_reviews()

    new_record = {
        "case_id": case_id.strip(),
        "decision": decision_clean,
        "corrected_diagnosis": corrected_diagnosis.strip(),
        "explanation": explanation.strip(),
        "reviewer": reviewer.strip() or "Anonymous Reviewer",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # If already reviewed, update the existing entry; otherwise append
    if case_id in df["case_id"].values:
        idx = df[df["case_id"] == case_id].index[-1]
        for k, v in new_record.items():
            df.at[idx, k] = v
    else:
        new_df = pd.DataFrame([new_record])
        df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv(REVIEWS_FILE, index=False, encoding="utf-8")
    return new_record


def calculate_review_metrics(reviews_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Compute official human-in-the-loop oversight metrics:
      AI Agreement Rate = Accepted Cases / Total Reviewed Cases * 100
      Correction Rate   = (Edited + Rejected) / Total Reviewed Cases * 100
    """
    df = reviews_df if reviews_df is not None else load_reviews()

    total_reviewed = len(df)
    if total_reviewed == 0:
        return {
            "total_reviewed": 0,
            "accepted_count": 0,
            "edited_count": 0,
            "rejected_count": 0,
            "agreement_rate": 0.0,
            "correction_rate": 0.0,
        }

    counts = df["decision"].value_counts().to_dict()
    accepted = counts.get(REVIEW_STATUS_ACCEPTED, 0)
    edited = counts.get(REVIEW_STATUS_EDITED, 0)
    rejected = counts.get(REVIEW_STATUS_REJECTED, 0)

    agreement_rate = round((accepted / total_reviewed) * 100.0, 1)
    correction_rate = round(((edited + rejected) / total_reviewed) * 100.0, 1)

    return {
        "total_reviewed": total_reviewed,
        "accepted_count": accepted,
        "edited_count": edited,
        "rejected_count": rejected,
        "agreement_rate": agreement_rate,
        "correction_rate": correction_rate,
    }
