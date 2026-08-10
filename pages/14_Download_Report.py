"""Download Report — assemble and export the final PDF report."""

import streamlit as st

from reports.pdf_generator import ReportGenerator
from utils.constants import EXPORTS_PDF_DIR
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("📄 Download Report")

if not require_step("llm_summary"):
    st.stop()

st.write(
    "Generate a PDF report covering the layout, grid, heatmaps, charts, "
    "metrics, Gemini summary, and recommendations for this run."
)

run_id = st.session_state.get("run_id", "run")

if st.button("Generate PDF Report", type="primary", icon="📄"):
    context = {
        "run_id": run_id,
        "mission": st.session_state.get("mission_profile"),
        "grid": st.session_state.get("occupancy_grid"),
        "hacking_report": st.session_state.get("hacking_report"),
        "llm_summary": st.session_state.get("llm_summary"),
    }
    try:
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
        with open(output_path, "rb") as report_file:
            st.download_button(
                "Download PDF",
                data=report_file.read(),
                file_name=f"{run_id}.pdf",
                mime="application/pdf",
            )
    except NotImplementedError:
        st.info(
            "PDF report generation is not implemented yet — see "
            "`reports/pdf_generator.py` and PROJECT_PLAN.md, Phase 9."
        )

st.divider()
st.caption("Other export formats (PNG, CSV, JSON) are available from the Explainability Dashboard once implemented.")
