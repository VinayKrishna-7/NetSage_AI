"""
app.py
==============================================================================
NetSage AI: AI-Assisted Network Troubleshooting with Human Review
==============================================================================
Interactive Streamlit application implementing evidence-based troubleshooting
for Cisco Packet Tracer and enterprise networking labs.

Sections:
 1. Home
 2. Case Dataset
 3. Troubleshoot a Case
 4. AI Diagnosis
 5. Python Rule Checker
 6. Human Review
 7. Responsible AI Log
 8. Dashboard
 9. About Project
"""

import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

# NetSage AI Core Modules
from config import (
    ALLOWED_REVIEW_DECISIONS,
    NETSAGE_MODE,
    OPENAI_API_KEY,
    REVIEW_STATUS_ACCEPTED,
    REVIEW_STATUS_EDITED,
    REVIEW_STATUS_REJECTED,
    SAFETY_DISCLAIMER,
    is_mock_mode,
)
from data_loader import (
    get_case_by_id,
    list_case_ids,
    load_cases,
    load_responsible_ai_log,
    load_reviews,
    load_viva_qa,
)
from rule_checker import (
    check_apipa_address,
    check_gateway_in_subnet,
    check_valid_ip,
    check_valid_subnet_mask,
    get_osi_layer_breakdown,
    run_all_checks,
)
from ai_diagnosis import (
    diagnose_case,
    load_system_prompt,
    build_user_prompt,
    validate_ai_response,
)
from reviewer import (
    calculate_review_metrics,
    get_review_for_case,
    record_review,
)
from dashboard.dashboard import render_dashboard

# -----------------------------------------------------------------------------
# Streamlit Page Setup & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NetSage AI - Network Troubleshooting",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for academic cards and badges
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border-left: 5px solid #3b82f6;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .safety-banner {
        background-color: #fffbeb;
        border-left: 6px solid #f59e0b;
        padding: 12px 18px;
        border-radius: 6px;
        color: #92400e;
        font-weight: 500;
        margin-bottom: 16px;
    }
    .badge-accepted {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-edited {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-rejected {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Global Data Caching
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_cases_data():
    return load_cases()

try:
    cases_df = fetch_cases_data()
except Exception as e:
    st.error(f"Error loading cases.csv: {e}")
    cases_df = pd.DataFrame()

reviews_df = load_reviews()
responsible_df = load_responsible_ai_log()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌐 NETSAGE AI")
    st.caption("AI-Assisted Network Troubleshooting with Human Review")
    st.markdown("---")

    # Mode Indicator
    current_mock = is_mock_mode()
    mode_text = "🟢 MOCK / DEMO MODE" if current_mock else "🔵 LIVE API MODE"
    st.info(f"**Operating Mode:** {mode_text}\n\n*(Zero-cost offline demo mode enabled for viva & Packet Tracer labs)*")

    # Safety Notice
    st.markdown(
        """
        <div style='font-size: 0.82rem; color: #64748b; background: #f1f5f9; padding: 10px; border-radius: 6px;'>
        🛡️ <b>Safety Guardrail:</b><br>
        AI diagnosis is strictly advisory. Configuration changes are never automatically applied.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigation Menu",
        [
            "1. Home",
            "2. Case Dataset",
            "3. Troubleshoot a Case",
            "4. AI Diagnosis",
            "5. Python Rule Checker",
            "6. Human Review",
            "7. Responsible AI Log",
            "8. Dashboard",
            "9. About Project",
        ],
        index=0,
    )

    st.markdown("---")
    st.caption(f"Knowledge Base: **{len(cases_df)} Cases**")
    st.caption(f"Active Reviews: **{len(reviews_df)} Reviewed**")


# =============================================================================
# PAGE 1: HOME
# =============================================================================
if page == "1. Home":
    st.title("NetSage AI: Network Troubleshooting System")
    st.markdown("#### *AI-Assisted Network Fault Isolation Grounded in Cisco Packet Tracer Evidence*")

    st.markdown(
        f"""
        <div class="safety-banner">
        ⚠️ <b>Safety Policy:</b> {SAFETY_DISCLAIMER} Configurations are never automatically applied to lab hardware or Packet Tracer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    metrics = calculate_review_metrics(reviews_df)
    col1.metric("Troubleshooting Cases", len(cases_df), "32 Troubleshooting Cases")
    col2.metric("Deterministic Rules", "15 Rules", "Python ipaddress")
    col3.metric("AI Agreement Rate", f"{metrics['agreement_rate']}%", "Human Accepted")
    col4.metric("Correction Rate", f"{metrics['correction_rate']}%", "Edited / Rejected")

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("🎯 Project Purpose & Objectives")
        st.write(
            """
            In computer networking laboratories (such as **Cisco Packet Tracer** and CCNA curricula), 
            students and novice engineers frequently face complex connectivity failures spanning 
            multiple OSI layers.

            **NetSage AI** bridges artificial intelligence and deterministic networking principles by:
            1. **Evidence-Based Diagnosis:** Ingesting symptoms, topologies, IP configurations, and Cisco `show` command outputs.
            2. **Deterministic Verification:** Using deterministic Python validation for IP, subnet, and VLAN configuration.
            3. **Structured AI Diagnosis:** Generating root cause analysis, confidence scores, and recommended CLI commands.
            4. **Mandatory Human-in-the-Loop Review:** Allowing network instructors and engineers to **ACCEPT**, **EDIT**, or **REJECT** AI diagnoses.
            5. **Responsible AI Accountability:** Documenting AI errors and extracting educational lessons.
            """
        )

        st.subheader("🚀 Quick Start Guide")
        st.markdown(
            """
            - **Step 1:** Go to **'3. Troubleshoot a Case'** and pick any case (e.g. `NET001` or `NET005`).
            - **Step 2:** Review the symptom and Cisco `show` command evidence.
            - **Step 3:** Run the **Deterministic Rule Checker** to test IP and subnet correctness.
            - **Step 4:** Execute the **AI Diagnosis** engine (works offline in Mock Mode).
            - **Step 5:** Act as human reviewer to **Accept**, **Edit**, or **Reject** the advice.
            - **Step 6:** Inspect the **Dashboard** and **Responsible AI Log** for audit metrics!
            """
        )

    with col_right:
        st.subheader("⚙️ System Architecture")
        st.markdown(
            """
            ```
            +-----------------------------------------------+
            |  Cisco Packet Tracer / Show Command Evidence  |
            +-----------------------+-----------------------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
            +-------------------+       +-------------------+
            | Python Rule       |       | NetSage AI Engine |
            | Checker (ipaddress|       | (Mock / OpenAI    |
            | deterministic)    |       | Structured JSON)  |
            +---------+---------+       +---------+---------+
                      |                           |
                      +-------------+-------------+
                                    |
                                    v
                     +-----------------------------+
                     |  Human Reviewer Oversight   |
                     |  [ACCEPT]  [EDIT]  [REJECT] |
                     +--------------+--------------+
                                    |
                                    v
                     +-----------------------------+
                     |  Responsible AI Audit Log   |
                     |  & Analytics Dashboard      |
                     +-----------------------------+
            ```
            """
        )


# =============================================================================
# PAGE 2: CASE DATASET
# =============================================================================
elif page == "2. Case Dataset":
    st.title("📚 Cisco Troubleshooting Case Dataset")
    st.caption("Comprehensive collection of 32 verified Packet Tracer scenarios covering 10 networking fault domains.")

    if cases_df.empty:
        st.warning("No cases found in data/cases.csv.")
    else:
        # Filter controls
        fcol1, fcol2, fcol3 = st.columns(3)
        fault_types = ["All"] + sorted(cases_df["expected_fault"].unique().tolist())
        severities = ["All"] + sorted(cases_df["severity"].unique().tolist())
        osi_layers = ["All"] + sorted(cases_df["osi_layer"].unique().tolist())

        selected_fault = fcol1.selectbox("Filter by Fault Domain", fault_types)
        selected_sev = fcol2.selectbox("Filter by Severity", severities)
        selected_osi = fcol3.selectbox("Filter by OSI Layer", osi_layers)

        filtered_df = cases_df.copy()
        if selected_fault != "All":
            filtered_df = filtered_df[filtered_df["expected_fault"] == selected_fault]
        if selected_sev != "All":
            filtered_df = filtered_df[filtered_df["severity"] == selected_sev]
        if selected_osi != "All":
            filtered_df = filtered_df[filtered_df["osi_layer"] == selected_osi]

        st.write(f"Showing **{len(filtered_df)}** of **{len(cases_df)}** cases:")

        # Summary Table
        summary_view = filtered_df[
            ["case_id", "title", "expected_fault", "osi_layer", "severity", "device", "expected_root_cause"]
        ]
        st.dataframe(summary_view, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Case Deep-Dive Inspector")
        case_ids = filtered_df["case_id"].tolist()
        if case_ids:
            inspect_id = st.selectbox("Select Case ID to Inspect", case_ids)
            case_data = get_case_by_id(inspect_id, cases_df)
            if case_data:
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.markdown(f"### {case_data['case_id']}: {case_data['title']}")
                    st.markdown(f"**Fault Domain:** `{case_data['expected_fault']}` | **Severity:** `{case_data['severity']}`")
                    st.markdown(f"**OSI Layer:** `{case_data['osi_layer']}` | **Concept:** `{case_data['concept']}`")
                    st.info(f"**Reported Symptom:**\n{case_data['symptom']}")
                    st.markdown(f"**Topology:** `{case_data['topology']}`")
                    st.markdown(f"**Target Device:** `{case_data['device']}`")

                with c_col2:
                    st.markdown("#### Client Configuration")
                    st.code(case_data["client_configuration"], language="text")
                    st.markdown(f"#### Show Command: `#{case_data['show_command']}`")
                    st.code(case_data["show_output"], language="cisco")
                    st.markdown("#### Expected Fix")
                    st.code(case_data["expected_fix"], language="cisco")


# =============================================================================
# PAGE 3: TROUBLESHOOT A CASE (CORE WORKBENCH)
# =============================================================================
elif page == "3. Troubleshoot a Case":
    st.title("🛠️ Interactive Troubleshooting Workbench")
    st.caption("Diagnose Cisco Packet Tracer scenarios using Rule Checker and AI with mandatory Human Review.")

    st.markdown(
        f"""
        <div class="safety-banner">
        ⚠️ <b>Safety Notice:</b> {SAFETY_DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_case_ids = list_case_ids(cases_df)
    selected_case_id = st.selectbox(
        "Choose a Case ID to Troubleshoot",
        all_case_ids,
        format_func=lambda cid: f"{cid} - {get_case_by_id(cid, cases_df)['title']}",
    )

    case_info = get_case_by_id(selected_case_id, cases_df)

    if case_info:
        # Case Details Display
        with st.expander("📋 View Case Scenario & Evidence Details", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"### {case_info['case_id']} - {case_info['title']}")
                st.markdown(f"**Symptom:** {case_info['symptom']}")
                st.markdown(f"**Topology:** `{case_info['topology']}`")
                st.markdown(f"**Device:** `{case_info['device']}` | **Severity:** `{case_info['severity']}`")
            with col_b:
                st.markdown("**Client IP Settings:**")
                st.code(case_info["client_configuration"], language="text")
                st.markdown(f"**Show Command:** `{case_info['show_command']}`")
                st.code(case_info["show_output"], language="cisco")

        # Visual Topology Link Path Bar
        st.markdown(
            f"""
            <div style='background: #f8fafc; border-left: 4px solid #0284c7; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;'>
                <span style='font-size: 0.85rem; font-weight: 700; color: #0369a1;'>🌐 TOPOLOGY PATH:</span> 
                <span style='font-family: monospace; font-size: 0.95rem; color: #0f172a;'>{case_info['topology']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Action Buttons
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            run_rules = st.button("⚡ Run Deterministic Rule Checker", use_container_width=True, type="secondary")
        with act_col2:
            run_ai = st.button("🤖 Run AI Diagnosis Engine", use_container_width=True, type="primary")

        # Session state storage for this case
        if f"rule_results_{selected_case_id}" not in st.session_state and run_rules:
            st.session_state[f"rule_results_{selected_case_id}"] = run_all_checks(case_info)

        if f"ai_diagnosis_{selected_case_id}" not in st.session_state and run_ai:
            with st.spinner("Analyzing show command outputs and generating structured diagnosis..."):
                st.session_state[f"ai_diagnosis_{selected_case_id}"] = diagnose_case(case_info)

        # Display Rule Checker Results if available
        if f"rule_results_{selected_case_id}" in st.session_state:
            rc = st.session_state[f"rule_results_{selected_case_id}"]
            st.subheader("⚡ Deterministic Rule Checker Results")
            r_c1, r_c2, r_c3 = st.columns(3)
            r_c1.metric("Checks Evaluated", rc["total_checks"])
            r_c2.metric("Passed Checks", rc["pass_count"])
            r_c3.metric("Rule Violations", rc["fail_count"], delta=f"-{rc['fail_count']}" if rc["fail_count"] > 0 else "0", delta_color="inverse")

            if rc["failures"]:
                st.error("🚨 Deterministic Rule Violations Found:")
                for f in rc["failures"]:
                    st.markdown(f"- **{f['check'].upper()}**: {f['message']} `(Evidence: {f['evidence']})`")
            else:
                st.success("✅ No low-level IP/subnet/interface syntax rule violations detected.")

            # Bottom-Up OSI Layer Diagnostic Ladder
            osi_breakdown = get_osi_layer_breakdown(case_info)
            with st.expander("📶 Step-by-Step OSI Layer Diagnostic Ladder", expanded=True):
                st.caption("Bottom-Up Layer Verification (Physical ➔ Data Link ➔ Network ➔ Transport ➔ Application):")
                lad_c1, lad_c2, lad_c3, lad_c4, lad_c5 = st.columns(5)
                layers_ordered = [
                    ("Layer 1 - Physical", lad_c1),
                    ("Layer 2 - Data Link", lad_c2),
                    ("Layer 3 - Network", lad_c3),
                    ("Layer 4 - Transport", lad_c4),
                    ("Layer 7 - Application", lad_c5),
                ]
                for l_name, l_col in layers_ordered:
                    l_data = osi_breakdown.get(l_name, {"status": "NOT_TESTED", "message": "N/A"})
                    l_status = l_data["status"]
                    with l_col:
                        if l_status == "PASS":
                            st.success(f"**{l_name.split(' - ')[0]}**\n\n🟢 PASS")
                        elif l_status == "FAIL":
                            st.error(f"**{l_name.split(' - ')[0]}**\n\n🔴 FAIL")
                        elif l_status == "WARNING":
                            st.warning(f"**{l_name.split(' - ')[0]}**\n\n🟡 WARN")
                        else:
                            st.info(f"**{l_name.split(' - ')[0]}**\n\n⚪ N/A")
                        st.caption(l_data["message"])

        st.markdown("---")

        # Display AI Diagnosis Results if available
        ai_diag = st.session_state.get(f"ai_diagnosis_{selected_case_id}")
        if ai_diag:
            st.subheader("🤖 AI-Generated Diagnosis (Advisory)")

            conf_color = "green" if ai_diag["confidence"] == "HIGH" else ("orange" if ai_diag["confidence"] == "MEDIUM" else "red")
            st.markdown(
                f"""
                <div class="metric-card">
                <span style="font-size: 1.25rem; font-weight: bold;">Root Cause:</span> {ai_diag['root_cause']}<br>
                <b>Confidence:</b> <span style="color: {conf_color}; font-weight: 700;">{ai_diag['confidence']} ({ai_diag['confidence_score']}%)</span> | 
                <b>OSI Layer:</b> <code>{ai_diag['osi_layer']}</code> | 
                <b>Concept:</b> <i>{ai_diag['concept']}</i>
                </div>
                """,
                unsafe_allow_html=True,
            )

            d_c1, d_c2 = st.columns(2)
            with d_c1:
                st.markdown("#### 🔍 Cited Evidence from Show Output")
                for ev in ai_diag.get("evidence", []):
                    st.markdown(f"- {ev}")

                st.markdown("#### 🔭 Recommended Next Diagnostic Commands")
                for cmd in ai_diag.get("next_commands", []):
                    st.code(cmd, language="cisco")

            with d_c2:
                st.markdown("#### 🛠️ Recommended Cisco Fix (Manual Review Required)")
                st.code(ai_diag.get("recommended_fix", ""), language="cisco")

                if ai_diag.get("alternative_causes"):
                    st.markdown("#### ⚠️ Alternative Hypotheses Considered")
                    for alt in ai_diag["alternative_causes"]:
                        st.markdown(f"- {alt}")

            if "_mock_note" in ai_diag:
                st.warning(f"💡 **Responsible AI Educational Note:** {ai_diag['_mock_note']}")

        st.markdown("---")

        # Human-in-the-Loop Review Submission Form
        st.subheader("👨‍💻 Mandatory Human Review Submission")
        existing_rev = get_review_for_case(selected_case_id)

        if existing_rev:
            badge_class = f"badge-{existing_rev['decision'].lower()}"
            st.markdown(
                f"Current Review Status: <span class='{badge_class}'>{existing_rev['decision']}</span> by **{existing_rev['reviewer']}** on *{existing_rev['timestamp']}*",
                unsafe_allow_html=True,
            )
            if existing_rev["corrected_diagnosis"]:
                st.markdown(f"**Human Corrected Diagnosis:** {existing_rev['corrected_diagnosis']}")
            if existing_rev["explanation"]:
                st.markdown(f"**Explanation:** {existing_rev['explanation']}")

        with st.form(f"review_form_{selected_case_id}"):
            st.write("Submit or modify human review decision for this diagnosis:")
            reviewer_name = st.text_input("Reviewer Name / Student ID", value=existing_rev["reviewer"] if existing_rev else "Alice Chen (Student)")
            decision = st.selectbox(
                "Human Review Decision",
                ALLOWED_REVIEW_DECISIONS,
                index=ALLOWED_REVIEW_DECISIONS.index(existing_rev["decision"]) if existing_rev else 0,
            )
            corrected_diag = st.text_area(
                "Corrected Diagnosis (Required if EDITED or REJECTED)",
                value=existing_rev["corrected_diagnosis"] if existing_rev else "",
                placeholder="Enter the technically correct root cause if AI was flawed...",
            )
            explanation = st.text_area(
                "Reviewer Engineering Explanation",
                value=existing_rev["explanation"] if existing_rev else "",
                placeholder="Explain why this decision was taken and cite the definitive evidence...",
            )
            submit_rev = st.form_submit_button("💾 Save Human Review Decision", type="primary")

            if submit_rev:
                if decision in [REVIEW_STATUS_EDITED, REVIEW_STATUS_REJECTED] and not corrected_diag.strip():
                    st.error("Please provide a Corrected Diagnosis when marking a case as EDITED or REJECTED.")
                else:
                    record_review(
                        case_id=selected_case_id,
                        decision=decision,
                        corrected_diagnosis=corrected_diag,
                        explanation=explanation,
                        reviewer=reviewer_name,
                    )
                    st.success(f"Review for case {selected_case_id} recorded as **{decision}**!")
                    st.rerun()

        # Export Case Troubleshooting Investigation Report & Packet Tracer Fix Box
        st.markdown("---")
        exp_col1, exp_col2 = st.columns([1.2, 1])
        with exp_col1:
            st.markdown("#### 📄 Case Diagnostic Audit Report")
            st.caption("Generate a formatted lab investigation report for viva defense:")
            ai_diag_val = st.session_state.get(f"ai_diagnosis_{selected_case_id}")
            report_md = f"""# NetSage AI - Troubleshooting Investigation Report
## Case ID: {case_info['case_id']} - {case_info['title']}

- **Generated Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Target Device:** `{case_info['device']}`
- **Fault Domain:** `{case_info['expected_fault']}` | **Severity:** `{case_info['severity']}`
- **OSI Layer:** `{case_info['osi_layer']}` | **Concept:** `{case_info['concept']}`

---
### 1. Reported Network Symptom
> {case_info['symptom']}

### 2. Topology Link Path
`{case_info['topology']}`

### 3. Client Configuration
```text
{case_info['client_configuration']}
```

### 4. Cisco CLI Show-Command Evidence
```cisco
# {case_info['show_command']}
{case_info['show_output']}
```

### 5. Deterministic Rule Checker Status
- **Overall Status:** {st.session_state.get(f'rule_results_{selected_case_id}', {}).get('overall_status', 'Evaluated upon execution')}

### 6. AI Advisory Diagnosis
- **Diagnosed Root Cause:** {ai_diag_val.get('root_cause', 'Not evaluated in this session') if ai_diag_val else 'Pending execution'}
- **Confidence:** {ai_diag_val.get('confidence', 'N/A') if ai_diag_val else 'N/A'} ({ai_diag_val.get('confidence_score', 'N/A') if ai_diag_val else 'N/A'}%)
- **Remediation CLI Commands:**
```cisco
{ai_diag_val.get('recommended_fix', case_info['expected_fix']) if ai_diag_val else case_info['expected_fix']}
```

### 7. Human Reviewer Verdict
- **Decision:** {existing_rev.get('decision', 'Pending Review') if existing_rev else 'Pending Review'}
- **Reviewer:** {existing_rev.get('reviewer', 'N/A') if existing_rev else 'N/A'}
- **Corrected Diagnosis:** {existing_rev.get('corrected_diagnosis', 'None') if existing_rev else 'None'}
- **Reviewer Explanation:** {existing_rev.get('explanation', 'None') if existing_rev else 'None'}

---
*Notice: AI diagnosis is advisory. Human review is mandatory. Configurations are never auto-applied.*
"""
            st.download_button(
                label=f"📥 Download Case {selected_case_id} Audit Report (.md)",
                data=report_md,
                file_name=f"NetSage_Report_{selected_case_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with exp_col2:
            st.markdown("#### 💻 Cisco Packet Tracer CLI Fix Snippet")
            st.caption("Apply these commands manually in Packet Tracer:")
            st.code(case_info.get("expected_fix", ""), language="cisco")



# =============================================================================
# PAGE 4: AI DIAGNOSIS
# =============================================================================
elif page == "4. AI Diagnosis":
    st.title("🤖 AI Diagnosis Engine & Schema Inspector")
    st.caption("Inspect the AI system prompts, test prompt construction, and validate JSON output schemas.")

    t1, t2, t3 = st.tabs(["System Prompt", "Prompt Formatter", "Schema Validator"])

    with t1:
        st.subheader("Master System Prompt (`prompts/diagnose_prompt.md`)")
        st.markdown("This prompt enforces evidence grounding, hallucination control, and structured JSON output:")
        st.code(load_system_prompt(), language="markdown")

    with t2:
        st.subheader("Prompt Construction Tester")
        cid = st.selectbox("Select Case to Format", list_case_ids(cases_df), key="prompt_test_cid")
        cdata = get_case_by_id(cid, cases_df)
        if cdata:
            st.markdown("**Constructed User Prompt:**")
            st.code(build_user_prompt(cdata), language="markdown")

    with t3:
        st.subheader("JSON Response Schema Validator")
        st.write("Test arbitrary JSON output against NetSage AI's required schema:")
        sample_json_text = st.text_area(
            "Paste JSON to Validate:",
            value=json.dumps(
                {
                    "case_id": "NET001",
                    "root_cause": "Port Fa0/2 placed in VLAN 20 instead of VLAN 10.",
                    "confidence": "HIGH",
                    "confidence_score": 95,
                    "osi_layer": "Layer 2 - Data Link",
                    "concept": "Access Port VLAN Membership",
                    "evidence": ["Fa0/2 is listed under VLAN 20 in show vlan brief"],
                    "next_commands": ["show interfaces FastEthernet0/2 switchport"],
                    "recommended_fix": "switchport access vlan 10",
                    "alternative_causes": ["Cabling issue"],
                    "needs_human_review": True,
                },
                indent=2,
            ),
            height=260,
        )

        if st.button("Validate JSON Schema"):
            try:
                parsed = json.loads(sample_json_text)
                valid, msg, cleaned = validate_ai_response(parsed)
                if valid:
                    st.success("✅ JSON response conforms to all schema requirements!")
                    st.json(cleaned)
                else:
                    st.error(f"❌ Validation Error: {msg}")
            except Exception as e:
                st.error(f"Invalid JSON string: {e}")


# =============================================================================
# PAGE 5: PYTHON RULE CHECKER
# =============================================================================
elif page == "5. Python Rule Checker":
    st.title("⚡ Python Deterministic Rule Checker")
    st.caption("Strict, non-AI networking verification using Python's `ipaddress` library and regex parsing.")

    st.write(
        """
        The Rule Checker guarantees deterministic evaluation of basic configuration parameters 
        before or alongside AI reasoning. It never hallucinates and yields unambiguous **PASS**, **FAIL**, or **WARNING** verdicts.
        """
    )

    t_case, t_custom = st.tabs(["Test Against Case Dataset", "Custom Manual IP/Gateway Checker"])

    with t_case:
        rc_cid = st.selectbox("Select Case for Batch Rule Execution", list_case_ids(cases_df), key="rc_tab_cid")
        c_obj = get_case_by_id(rc_cid, cases_df)
        if c_obj:
            results = run_all_checks(c_obj)
            st.markdown(f"### Results for `{rc_cid}`: Overall Status = **{results['overall_status']}**")

            r_col1, r_col2 = st.columns([1, 1.5])
            with r_col1:
                st.metric("Total Rules Tested", results["total_checks"])
                st.metric("Passed", results["pass_count"])
                st.metric("Violations / Failures", results["fail_count"])
                st.metric("Warnings", results["warning_count"])

            with r_col2:
                for chk in results["results"]:
                    status = chk["status"]
                    if status == "PASS":
                        st.success(f"**PASS [{chk['check']}]**: {chk['message']}")
                    elif status == "FAIL":
                        st.error(f"**FAIL [{chk['check']}]**: {chk['message']}\n\n*Evidence:* `{chk['evidence']}`")
                    else:
                        st.warning(f"**WARNING [{chk['check']}]**: {chk['message']}\n\n*Evidence:* `{chk['evidence']}`")

    with t_custom:
        st.subheader("Custom IP Subnet & Gateway Calculator")
        c_ip = st.text_input("Host IPv4 Address", "192.168.10.20")
        c_mask = st.text_input("Subnet Mask (Dotted Decimal or CIDR)", "255.255.255.0")
        c_gw = st.text_input("Default Gateway IPv4 Address", "192.168.20.1")

        if st.button("Run Deterministic IP Check", type="primary"):
            res_ip = check_valid_ip(c_ip)
            res_mask = check_valid_subnet_mask(c_mask)
            res_gw = check_gateway_in_subnet(c_ip, c_mask, c_gw)
            res_apipa = check_apipa_address(c_ip)

            st.write("---")
            st.markdown("#### Evaluation Results:")
            for r in [res_ip, res_mask, res_gw, res_apipa]:
                if r["status"] == "PASS":
                    st.success(f"**PASS [{r['check']}]**: {r['message']}")
                elif r["status"] == "FAIL":
                    st.error(f"**FAIL [{r['check']}]**: {r['message']}\n\n*Evidence:* `{r['evidence']}`")
                else:
                    st.warning(f"**WARNING [{r['check']}]**: {r['message']}")


# =============================================================================
# PAGE 6: HUMAN REVIEW
# =============================================================================
elif page == "6. Human Review":
    st.title("👨‍⚖️ Human-in-the-Loop Review Log & Audit Trail")
    st.caption("Comprehensive log of all human engineer decisions on AI diagnoses.")

    metrics = calculate_review_metrics(reviews_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviewed Cases", metrics["total_reviewed"])
    c2.metric("Accepted", metrics["accepted_count"])
    c3.metric("Edited", metrics["edited_count"])
    c4.metric("Rejected", metrics["rejected_count"])

    st.markdown("---")
    st.dataframe(reviews_df, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 7: RESPONSIBLE AI LOG
# =============================================================================
elif page == "7. Responsible AI Log":
    st.title("🛡️ Responsible AI & Failure Analysis Log")
    st.caption("Documenting cases where AI diagnoses were imperfect, erroneous, or hallucinated, and the lessons learned.")

    st.markdown(
        """
        In academic networking and enterprise deployments, **unsupervised AI is unsafe**.
        This log documents specific real-world cases where NetSage AI produced incorrect advice, 
        illustrating why **Human-in-the-Loop** review is essential.
        """
    )

    if responsible_df.empty:
        st.warning("No entries in data/responsible_ai_log.csv.")
    else:
        for idx, row in responsible_df.iterrows():
            with st.expander(f"Case {row['case_id']}: Human Decision = {row['human_decision']}", expanded=(idx == 0)):
                st.markdown(f"**Flawed AI Diagnosis:**\n> *\"{row['ai_diagnosis']}\"*")
                st.markdown(f"**Human Corrected Diagnosis:**\n> **{row['corrected_diagnosis']}**")
                st.markdown(f"**Why the AI Was Wrong:**\n{row['reason_ai_was_wrong']}")
                st.markdown(f"**Definitive Evidence Used by Reviewer:**\n`{row['evidence_used']}`")
                st.info(f"💡 **Engineering Lesson:**\n{row['lesson']}")


# =============================================================================
# PAGE 8: DASHBOARD
# =============================================================================
elif page == "8. Dashboard":
    render_dashboard(st, cases_df, reviews_df)


# =============================================================================
# PAGE 9: ABOUT PROJECT
# =============================================================================
elif page == "9. About Project":
    st.title("📖 About NetSage AI & Viva Preparation")
    st.caption("Academic Project Documentation, Interactive Viva Trainer, and Technical Specifications.")

    about_tab1, about_tab2, about_tab3 = st.tabs([
        "📋 Project Overview & Scope",
        "🎓 Interactive CCNA / Viva Quiz Trainer",
        "📐 System Architecture & Flowchart",
    ])

    with about_tab1:
        st.markdown(
            """
            ### Project Title
            **NetSage AI: AI-Assisted Network Troubleshooting with Human Review**

            ### Author & Academic Scope
            - **Domain:** Computer Networks, Packet Tracer Lab Automation, Responsible AI
            - **Target Audience:** Engineering Students, CCNA Candidates, Network Instructors
            - **Viva & Defense Ready:** Designed with full transparency, zero hidden keys, and deterministic rules.

            ### Key Technical Pillars
            1. **OSI Model Alignment:** Rigorously maps symptoms to Physical (L1), Data Link (L2), Network (L3), Transport (L4), and Application (L7) layers.
            2. **Advisory Stance:** The AI assistant provides evidence-grounded hypotheses; configuration changes are never automatically applied.
            3. **Deterministic Verification:** Mathematical subnet boundary, IP, and interface checks via Python's `ipaddress` library.
            4. **Offline Mock Mode:** Fully functional without requiring internet or paid API keys.
            5. **Responsible AI Accountability:** Explicitly tracks AI failure modes in a dedicated audit log.
            """
        )

    with about_tab2:
        st.subheader("🎓 CCNA & Academic Viva Practice Trainer")
        st.caption("Interactive study tool parsed directly from the 32 master defense questions in docs/viva_questions.md.")

        viva_items = load_viva_qa()
        if viva_items:
            sections = ["All Sections"] + sorted(list(set(item["section"] for item in viva_items)))
            sel_sec = st.selectbox("Filter Questions by Knowledge Domain:", sections)

            filtered_viva = viva_items if sel_sec == "All Sections" else [i for i in viva_items if i["section"] == sel_sec]
            st.write(f"Showing **{len(filtered_viva)}** questions in this domain:")

            viva_opts = [f"Q{i['id']}: {i['question']}" for i in filtered_viva]
            chosen_q_str = st.selectbox("Select a Question to Practice:", viva_opts)

            chosen_idx = viva_opts.index(chosen_q_str)
            chosen_item = filtered_viva[chosen_idx]

            st.markdown(f"### {chosen_item['question']}")
            st.caption(f"Knowledge Domain: `{chosen_item['section']}`")

            with st.expander("💡 Reveal Model Answer & Evaluation Key", expanded=False):
                st.markdown(f"> {chosen_item['answer']}")
                st.info("Tip for Viva: When answering, always emphasize *why* bottom-up OSI troubleshooting and evidence citation prevent configuration mistakes.")
        else:
            st.info("Viva questions will load from docs/viva_questions.md.")

    with about_tab3:
        st.subheader("📐 System Architecture & Data Flow")
        st.markdown(
            """
            ```
            +--------------------------------------------------------------------------+
            |                        Cisco Packet Tracer Lab                           |
            |       (Symptoms, Topology, IP Config, Show Command Output)               |
            +------------------------------------+-------------------------------------+
                                                 |
                                                 v
                                   [ NetSage Ingestion Layer ]
                                   (data_loader.py & config.py)
                                                 |
                        +------------------------+------------------------+
                        |                                                 |
                        v                                                 v
            +-----------------------+                         +-----------------------+
            | Python Rule Checker   |                         | AI Diagnosis Engine   |
            | (rule_checker.py)     |                         | (ai_diagnosis.py)     |
            | - Deterministic math  |                         | - System Prompt       |
            | - ipaddress module    |                         | - Mock Mode (Offline) |
            | - Regex state parsing |                         | - API Mode (LLM)      |
            | - Pass / Fail status  |                         | - JSON Schema Guard   |
            +-----------+-----------+                         +-----------+-----------+
                        |                                                 |
                        +------------------------+------------------------+
                                                 |
                                                 v
                              +-------------------------------------+
                              |   Human Reviewer Oversight Gate     |
                              |          (reviewer.py)              |
                              |     [ACCEPT]   [EDIT]   [REJECT]    |
                              +------------------+------------------+
                                                 |
                                                 v
                        +------------------------+------------------------+
                        |                                                 |
                        v                                                 v
            +-----------------------+                         +-----------------------+
            | Analytics Dashboard   |                         | Responsible AI Log    |
            | (dashboard.py)        |                         | (responsible_ai_log)  |
            | - Agreement Rate %    |                         | - Failure root cause  |
            | - Theme distribution  |                         | - Overlooked evidence |
            | - Excel export        |                         | - Engineering lessons |
            +-----------------------+                         +-----------------------+
            ```
            """
        )
