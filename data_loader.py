"""
data_loader.py
==============================================================================
NetSage AI - Data Loading and Dataset Management
==============================================================================
Loads, validates, and queries the Cisco networking troubleshooting cases
and human review logs.
"""

import re
from typing import Any, Dict, List, Optional
import pandas as pd
from config import CASES_FILE, DOCS_DIR, RESPONSIBLE_AI_LOG_FILE, REVIEWS_FILE

REQUIRED_CASE_COLUMNS = [
    "case_id",
    "title",
    "symptom",
    "topology",
    "device",
    "client_configuration",
    "show_command",
    "show_output",
    "expected_fault",
    "expected_root_cause",
    "osi_layer",
    "concept",
    "severity",
    "expected_next_command",
    "expected_fix",
    "expected_evidence",
]


def load_cases(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load the troubleshooting cases dataset from CSV.
    Validates that all expected columns are present.
    """
    path = csv_path or str(CASES_FILE)
    df = pd.read_csv(path, encoding="utf-8")
    missing_cols = [c for c in REQUIRED_CASE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Cases CSV is missing required columns: {missing_cols}")
    return df


def get_case_by_id(case_id: str, df: Optional[pd.DataFrame] = None) -> Optional[Dict]:
    """
    Retrieve a single case by its case_id as a dictionary.
    """
    if df is None:
        df = load_cases()
    matches = df[df["case_id"] == case_id]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def list_case_ids(df: Optional[pd.DataFrame] = None) -> List[str]:
    """
    Return a sorted list of all unique case IDs.
    """
    if df is None:
        df = load_cases()
    return sorted(df["case_id"].dropna().unique().tolist())


def load_responsible_ai_log(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load the Responsible AI review log where human review corrected AI diagnoses.
    """
    path = csv_path or str(RESPONSIBLE_AI_LOG_FILE)
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception:
        return pd.DataFrame(
            columns=[
                "case_id",
                "ai_diagnosis",
                "human_decision",
                "corrected_diagnosis",
                "reason_ai_was_wrong",
                "evidence_used",
                "lesson",
            ]
        )


def load_reviews(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load active reviewer records.
    """
    path = csv_path or str(REVIEWS_FILE)
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception:
        return pd.DataFrame(
            columns=[
                "case_id",
                "decision",
                "corrected_diagnosis",
                "explanation",
                "reviewer",
                "timestamp",
            ]
        )


def load_viva_qa() -> List[Dict[str, Any]]:
    """
    Parse the 32 viva voce questions and model answers from docs/viva_questions.md.
    Returns a list of dicts with keys: 'id', 'section', 'question', 'answer'.
    """
    viva_file = DOCS_DIR / "viva_questions.md"
    if not viva_file.exists():
        return []

    text = viva_file.read_text(encoding="utf-8")
    sections = re.split(r"(### SECTION \d+: [^\n]+)", text)

    items = []
    current_sec = "General Viva Preparation"

    for part in sections:
        if part.startswith("### SECTION"):
            current_sec = part.replace("###", "").strip()
            continue

        q_blocks = re.findall(
            r"####\s*(\d+)\.\s*(.*?)\n>\s*\*\*Answer:\*\*\s*(.*?)(?=\n####|\Z)",
            part,
            re.DOTALL,
        )
        for q_num, q_title, q_ans in q_blocks:
            items.append({
                "id": int(q_num),
                "section": current_sec,
                "question": f"{q_num}. {q_title.strip()}",
                "answer": q_ans.strip(),
            })

    return items

