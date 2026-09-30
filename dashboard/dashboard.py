"""
dashboard/dashboard.py
==============================================================================
NetSage AI - Analytics, Visualization & Metrics Dashboard
==============================================================================
Generates interactive charts, fault distribution summaries, and calculates:
 - AI Agreement Rate = Accepted Cases / Total Reviewed Cases * 100
 - Correction Rate   = (Edited + Rejected) / Total Reviewed Cases * 100
 - Breakdown by Fault Category, Severity, and OSI Layer
 - Excel & CSV multi-sheet compatible export
"""

from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from config import BASE_DIR, DATA_DIR
from reviewer import calculate_review_metrics, load_reviews
from rule_checker import run_all_checks


def get_dashboard_data(cases_df: pd.DataFrame, reviews_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Compile aggregated metrics for dashboard display."""
    if reviews_df is None:
        reviews_df = load_reviews()

    review_metrics = calculate_review_metrics(reviews_df)

    fault_counts = cases_df["expected_fault"].value_counts().to_dict()
    severity_counts = cases_df["severity"].value_counts().to_dict()
    osi_counts = cases_df["osi_layer"].value_counts().to_dict()

    return {
        "total_cases": len(cases_df),
        "review_metrics": review_metrics,
        "fault_counts": fault_counts,
        "severity_counts": severity_counts,
        "osi_counts": osi_counts,
        "reviews_df": reviews_df,
    }


def generate_excel_summary(cases_df: pd.DataFrame, reviews_df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """
    Generate an Excel-compatible (.xlsx or .csv) multi-table workbook containing
    theme analysis and human-AI agreement rates as required by the project specification.
    """
    if output_path is None:
        output_path = DATA_DIR / "netsage_summary_metrics.xlsx"

    metrics = calculate_review_metrics(reviews_df)

    kpi_df = pd.DataFrame([
        {"Metric": "Total Cases in Knowledge Base", "Value": len(cases_df)},
        {"Metric": "Total Cases Reviewed by Humans", "Value": metrics["total_reviewed"]},
        {"Metric": "AI Diagnoses Accepted", "Value": metrics["accepted_count"]},
        {"Metric": "AI Diagnoses Edited (Corrected)", "Value": metrics["edited_count"]},
        {"Metric": "AI Diagnoses Rejected", "Value": metrics["rejected_count"]},
        {"Metric": "AI Agreement Rate (%)", "Value": f"{metrics['agreement_rate']}%"},
        {"Metric": "Human Correction Rate (%)", "Value": f"{metrics['correction_rate']}%"},
    ])

    fault_df = cases_df["expected_fault"].value_counts().reset_index()
    fault_df.columns = ["Fault Domain / Theme", "Case Count"]

    osi_df = cases_df["osi_layer"].value_counts().reset_index()
    osi_df.columns = ["OSI Layer", "Case Count"]

    severity_df = cases_df["severity"].value_counts().reset_index()
    severity_df.columns = ["Severity Level", "Case Count"]

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            kpi_df.to_excel(writer, sheet_name="KPI & Agreement Rate", index=False)
            fault_df.to_excel(writer, sheet_name="Fault Domains", index=False)
            osi_df.to_excel(writer, sheet_name="OSI Layers", index=False)
            severity_df.to_excel(writer, sheet_name="Severity", index=False)
            reviews_df.to_excel(writer, sheet_name="Review Log", index=False)
    except Exception:
        # Fallback to CSV if openpyxl is not available
        csv_fallback = DATA_DIR / "netsage_summary_metrics.csv"
        kpi_df.to_csv(csv_fallback, index=False)
        return csv_fallback

    return output_path


def render_dashboard(st, cases_df: pd.DataFrame, reviews_df: pd.DataFrame):
    """
    Render the comprehensive dashboard within the Streamlit application.
    Displays metrics cards, Plotly charts, data tables, and export options.
    """
    st.title("Network Troubleshooting Analytics & Oversight Dashboard")
    st.caption("Empirical evaluation of AI diagnostic accuracy, human intervention rates, and networking fault themes.")

    data = get_dashboard_data(cases_df, reviews_df)
    rm = data["review_metrics"]

    # Top KPI Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Cases", data["total_cases"])
    c2.metric("Reviewed Cases", rm["total_reviewed"])
    c3.metric(
        "AI Agreement Rate",
        f"{rm['agreement_rate']}%",
        help="Accepted Cases / Total Reviewed Cases * 100",
    )
    c4.metric(
        "Human Correction Rate",
        f"{rm['correction_rate']}%",
        help="(Edited + Rejected) / Total Reviewed Cases * 100",
        delta=f"-{rm['correction_rate']}%" if rm["correction_rate"] > 0 else "0%",
        delta_color="inverse",
    )
    c5.metric("Decisions", f"{rm['accepted_count']}A / {rm['edited_count']}E / {rm['rejected_count']}R")

    st.markdown("---")

    # Review Decisions Breakdown Banner
    st.subheader("Human-in-the-Loop Review Status")
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.success(f"**Accepted Diagnoses:** {rm['accepted_count']}")
        st.caption("AI diagnosis was verified as accurate and evidence-grounded.")
    with rc2:
        st.warning(f"**Edited Diagnoses:** {rm['edited_count']}")
        st.caption("AI diagnosis required correction or refinement by human engineer.")
    with rc3:
        st.error(f"**Rejected Diagnoses:** {rm['rejected_count']}")
        st.caption("AI diagnosis was rejected due to hallucination or incorrect root cause.")

    st.markdown("---")

    # Graphical Visualizations
    col_left, col_right = st.columns(2)

    try:
        import plotly.express as px

        with col_left:
            st.subheader("Cases by Networking Fault Domain")
            fault_df = cases_df["expected_fault"].value_counts().reset_index()
            fault_df.columns = ["Fault Domain", "Count"]
            fig_fault = px.bar(
                fault_df,
                x="Fault Domain",
                y="Count",
                color="Fault Domain",
                title="Troubleshooting Cases by Fault Domain",
                text="Count",
            )
            fig_fault.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_fault, use_container_width=True)

            st.subheader("Cases by Severity")
            sev_df = cases_df["severity"].value_counts().reset_index()
            sev_df.columns = ["Severity", "Count"]
            color_map = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
            fig_sev = px.pie(
                sev_df,
                names="Severity",
                values="Count",
                title="Fault Distribution by Severity",
                color="Severity",
                color_discrete_map=color_map,
                hole=0.4,
            )
            st.plotly_chart(fig_sev, use_container_width=True)

        with col_right:
            st.subheader("Cases by OSI Layer")
            osi_df = cases_df["osi_layer"].value_counts().reset_index()
            osi_df.columns = ["OSI Layer", "Count"]
            fig_osi = px.bar(
                osi_df,
                y="OSI Layer",
                x="Count",
                orientation="h",
                color="OSI Layer",
                title="Troubleshooting Cases Across OSI Stack",
                text="Count",
            )
            fig_osi.update_layout(showlegend=False)
            st.plotly_chart(fig_osi, use_container_width=True)

            st.subheader("Human Review Decisions Distribution")
            rev_summary = pd.DataFrame([
                {"Decision": "Accepted", "Count": rm["accepted_count"], "Color": "#22c55e"},
                {"Decision": "Edited", "Count": rm["edited_count"], "Color": "#eab308"},
                {"Decision": "Rejected", "Count": rm["rejected_count"], "Color": "#ef4444"},
            ])
            fig_dec = px.pie(
                rev_summary,
                names="Decision",
                values="Count",
                title="Human Review Decisions",
                color="Decision",
                color_discrete_map={"Accepted": "#22c55e", "Edited": "#eab308", "Rejected": "#ef4444"},
                hole=0.4,
            )
            st.plotly_chart(fig_dec, use_container_width=True)

    except ImportError:
        st.info("Interactive Plotly charts are loading or Matplotlib fallback is enabled.")

    st.markdown("---")

    # Detailed Summary Table & Export Options
    st.subheader("Spreadsheet Export & Comprehensive Summary")
    st.write(
        "Download an Excel or CSV summary containing the theme breakdown, human agreement metrics, and audit log for viva presentation."
    )

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        if st.button("Generate Summary Spreadsheet", key="btn_gen_summary"):
            summary_file = generate_excel_summary(cases_df, reviews_df)
            st.success(f"Summary spreadsheet generated: `{summary_file.name}`")
            with open(summary_file, "rb") as f:
                st.download_button(
                    label=f"Download {summary_file.name}",
                    data=f,
                    file_name=summary_file.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    if summary_file.suffix == ".xlsx"
                    else "text/csv",
                )

    with exp_col2:
        st.markdown(
            f"""
        **Official Academic Metrics:**
        - **Total Dataset Size:** `{data['total_cases']}` realistic cases
        - **Total Active Reviews:** `{rm['total_reviewed']}`
        - **AI Agreement Rate:** `Accepted / Total = {rm['agreement_rate']}%`
        - **Human Correction Rate:** `(Edited + Rejected) / Total = {rm['correction_rate']}%`
        """
        )
