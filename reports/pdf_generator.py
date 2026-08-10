"""PDF report assembly via ReportLab.

Report contents: Layout, Grid, Heatmaps, Charts, Metrics, Gemini Summary,
Recommendations — see PROJECT_PLAN.md, Phase 9.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate


class ReportGenerator:
    """Builds the downloadable PDF report from a completed analysis run.

    Usage (once implemented)::

        report = ReportGenerator(run_context)
        report.add_layout_section()
        report.add_grid_section()
        report.add_heatmaps_section()
        report.add_charts_section()
        report.add_metrics_section()
        report.add_summary_section()
        report.add_recommendations_section()
        report.generate(output_path)
    """

    def __init__(self, context: dict[str, Any]) -> None:
        self.context = context
        self._story: list[Any] = []

    def add_layout_section(self) -> None:
        """Add the uploaded mission layout image.

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_layout_section is not yet implemented.")

    def add_grid_section(self) -> None:
        """Add the extracted/annotated occupancy grid.

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_grid_section is not yet implemented.")

    def add_heatmaps_section(self) -> None:
        """Add rendered heatmap images.

        TODO(reports): implement, exporting each Plotly figure to PNG
        first via ``reports.export_utils.export_png``.
        """
        raise NotImplementedError("ReportGenerator.add_heatmaps_section is not yet implemented.")

    def add_charts_section(self) -> None:
        """Add rendered training charts.

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_charts_section is not yet implemented.")

    def add_metrics_section(self) -> None:
        """Add a summary table of key metrics (coverage, hacking flags, etc).

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_metrics_section is not yet implemented.")

    def add_summary_section(self) -> None:
        """Add the Gemini-generated natural-language summary.

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_summary_section is not yet implemented.")

    def add_recommendations_section(self) -> None:
        """Add actionable recommendations derived from the hacking report.

        TODO(reports): implement.
        """
        raise NotImplementedError("ReportGenerator.add_recommendations_section is not yet implemented.")

    def generate(self, output_path: Path) -> Path:
        """Render the accumulated story to a PDF file at ``output_path``.

        TODO(reports): implement using ``SimpleDocTemplate`` / ``A4``.
        """
        raise NotImplementedError("ReportGenerator.generate is not yet implemented.")
