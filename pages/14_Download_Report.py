"""Download Report — assemble and export the final PDF report."""

import json
import streamlit as st

from reports.export_utils import export_csv, export_json
from reports.pdf_generator import ReportGenerator
from utils.constants import EXPORTS_PDF_DIR
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("📄 Download Report")

if not require_step("llm_summary"):
    st.stop()

st.write(
    "Generate a comprehensive PDF report covering the layout, grid, heatmaps, charts, "
    "metrics, Gemini summary, and recommendations for this run."
)

run_id = st.session_state.get("run_id", "run")

if st.button("Generate PDF Report", type="primary", icon="📄"):
    context = {
        "run_id": run_id,
        "mission": st.session_state.get("mission_profile"),
        "grid": st.session_state.get("occupancy_grid"),
        "annotation": st.session_state.get("annotation"),
        "layout_image": st.session_state.get("uploaded_image"),
        "training_logs": st.session_state.get("training_logs"),
        "hacking_report": st.session_state.get("hacking_report"),
        "llm_summary": st.session_state.get("llm_summary"),
    }
    try:
        with st.spinner("Assembling multi-page PDF report..."):
            report = ReportGenerator(context)
            report.add_layout_section()
            report.add_grid_section()
            report.add_heatmaps_section()
            report.add_charts_section()
            report.add_metrics_section()
            report.add_summary_section()
            report.add_recommendations_section()
            output_path = report.generate(EXPORTS_PDF_DIR / f"{run_id}.pdf")
            mark_step_complete("download_report")
            st.success(f"PDF Report generated successfully: `{output_path.name}`")

        with open(output_path, "rb") as report_file:
            st.download_button(
                "⬇️ Download PDF Report",
                data=report_file.read(),
                file_name=f"{run_id}.pdf",
                mime="application/pdf",
                type="primary",
            )
    except Exception as error:
        st.error(f"Error generating PDF report: {error}")

st.divider()
st.subheader("📦 Additional Data Exports")
st.write("Export raw training logs and policy inspection data for external analysis.")

col1, col2 = st.columns(2)

with col1:
    logger = st.session_state.get("training_logs")
    if logger and logger.get_logs():
        csv_path = logger.export_csv(EXPORTS_PDF_DIR.parent / "csv" / f"{run_id}_training_logs.csv")
        with open(csv_path, "rb") as f:
            st.download_button(
                "📊 Download Training Logs (CSV)",
                data=f.read(),
                file_name=f"{run_id}_training_logs.csv",
                mime="text/csv",
            )

with col2:
    report = st.session_state.get("hacking_report")
    if report:
        report_dict = {
            "run_id": run_id,
            "coverage_score": getattr(report, "coverage_score", 0.0),
            "is_hacking_suspected": getattr(report, "is_hacking_suspected", False),
            "findings": getattr(report, "notes", []),
            "llm_summary": st.session_state.get("llm_summary", ""),
        }
        json_path = export_json(report_dict, f"{run_id}_report.json")
        with open(json_path, "rb") as f:
            st.download_button(
                "📝 Download Analysis Report (JSON)",
                data=f.read(),
                file_name=f"{run_id}_report.json",
                mime="application/json",
            )

