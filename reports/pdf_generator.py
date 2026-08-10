"""PDF report assembly via ReportLab.

Report contents: Layout, Grid, Heatmaps, Charts, Metrics, Gemini Summary,
Recommendations — see PROJECT_PLAN.md, Phase 9.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from reports.export_utils import export_png
from utils.constants import CHART_TYPES, HEATMAP_TYPES
from utils.file_io import save_json
from vision.grid_extractor import GridExtractor
from visualization.charts import CHART_RENDERERS
from visualization.heatmaps import HEATMAP_RENDERERS


class ReportGenerator:
    """Builds the downloadable PDF report from a completed analysis run."""

    def __init__(self, context: dict[str, Any]) -> None:
        self.context = context
        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=12,
        )

        self.h2_style = ParagraphStyle(
            "ReportH2",
            parent=self.styles["Heading2"],
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=8,
        )

        self.body_style = ParagraphStyle(
            "ReportBody",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )

        self.bullet_style = ParagraphStyle(
            "ReportBullet",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            leftIndent=15,
            spaceAfter=4,
        )

        self._story: list[Any] = []
        self._init_header()

    def _init_header(self) -> None:
        run_id = self.context.get("run_id", "run")
        mission = self.context.get("mission")
        mission_name = mission.display_name if mission else "Standard Navigation"

        self._story.append(Paragraph("XRL Studio — Explainability & Safety Report", self.title_style))
        self._story.append(
            Paragraph(f"<b>Run ID:</b> {run_id} | <b>Mission Profile:</b> {mission_name}", self.body_style)
        )
        self._story.append(Spacer(1, 10))

    def add_layout_section(self) -> None:
        """Add the uploaded mission layout image."""
        self._story.append(Paragraph("1. Mission Layout Setup", self.h2_style))
        layout_image = self.context.get("layout_image")

        if layout_image is not None and isinstance(layout_image, np.ndarray):
            try:
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                pil_img = PILImage.fromarray(layout_image.astype(np.uint8))
                pil_img.save(temp_file.name)
                self._story.append(Image(temp_file.name, width=280, height=200))
                self._story.append(Spacer(1, 8))
            except Exception:
                self._story.append(Paragraph("Raw layout image provided.", self.body_style))
        else:
            mission = self.context.get("mission")
            desc = mission.description if mission else "Custom grid world layout."
            self._story.append(Paragraph(f"<b>Environment Description:</b> {desc}", self.body_style))

    def add_grid_section(self) -> None:
        """Add the extracted/annotated occupancy grid."""
        self._story.append(Paragraph("2. Extracted Occupancy Grid & Annotations", self.h2_style))
        grid = self.context.get("grid")

        if grid is not None and isinstance(grid, np.ndarray):
            annotation = self.context.get("annotation")
            rgb_preview = GridExtractor().visualize_grid(grid, annotation)

            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            pil_img = PILImage.fromarray(rgb_preview.astype(np.uint8))
            pil_img.save(temp_file.name)

            self._story.append(Image(temp_file.name, width=240, height=240))

            rows, cols = grid.shape
            from rl.environment import OBSTACLE

            obstacles = int((grid == OBSTACLE).sum())
            free_space = int(grid.size - obstacles)

            info_text = (
                f"<b>Grid Dimensions:</b> {rows}×{cols} ({grid.size} cells)<br/>"
                f"<b>Obstacle Cells:</b> {obstacles} | <b>Free Space Cells:</b> {free_space}"
            )
            self._story.append(Paragraph(info_text, self.body_style))
            self._story.append(Spacer(1, 10))

    def add_heatmaps_section(self) -> None:
        """Add rendered heatmap images."""
        self._story.append(PageBreak())
        self._story.append(Paragraph("3. Behavioural Heatmaps Analysis", self.h2_style))

        grid = self.context.get("grid")
        logger = self.context.get("training_logs")
        run_id = self.context.get("run_id", "run")

        if grid is not None and logger is not None:
            for heatmap_type in HEATMAP_TYPES:
                try:
                    fig = HEATMAP_RENDERERS[heatmap_type](grid, logger)
                    png_path = export_png(fig, f"{run_id}_heatmap_{heatmap_type}.png")
                    self._story.append(Paragraph(f"<b>Heatmap:</b> {heatmap_type.replace('_', ' ').title()}", self.body_style))
                    self._story.append(Image(str(png_path), width=340, height=280))
                    self._story.append(Spacer(1, 8))
                except Exception as err:
                    self._story.append(Paragraph(f"Could not render {heatmap_type} heatmap: {err}", self.body_style))

    def add_charts_section(self) -> None:
        """Add rendered training performance charts."""
        self._story.append(PageBreak())
        self._story.append(Paragraph("4. Training Performance Metrics & Charts", self.h2_style))

        grid = self.context.get("grid")
        logger = self.context.get("training_logs")
        run_id = self.context.get("run_id", "run")

        if logger is not None and grid is not None:
            for chart_type in CHART_TYPES:
                try:
                    fig = CHART_RENDERERS[chart_type](logger, grid)
                    png_path = export_png(fig, f"{run_id}_chart_{chart_type}.png")
                    self._story.append(Paragraph(f"<b>Chart:</b> {chart_type.replace('_', ' ').title()}", self.body_style))
                    self._story.append(Image(str(png_path), width=340, height=220))
                    self._story.append(Spacer(1, 8))
                except Exception as err:
                    self._story.append(Paragraph(f"Could not render {chart_type} chart: {err}", self.body_style))

    def add_metrics_section(self) -> None:
        """Add a summary table of key metrics (coverage, hacking flags, etc)."""
        self._story.append(Paragraph("5. Behavioral Summary & Safety Verification", self.h2_style))
        report = self.context.get("hacking_report")
        logger = self.context.get("training_logs")

        episodes = logger.get_logs() if logger else []
        total_ep = len(episodes)
        final_reward = f"{episodes[-1].total_reward:.2f}" if episodes else "0.00"

        cov_score = f"{getattr(report, 'coverage_score', 0.0):.2%}" if report else "N/A"
        is_hacking = getattr(report, "is_hacking_suspected", False) if report else False
        hacking_verdict = "⚠️ SUSPECTED" if is_hacking else "✅ CLEAN RUN"

        table_data = [
            ["Metric", "Value"],
            ["Total Episodes Trained", str(total_ep)],
            ["Final Episode Reward", final_reward],
            ["Cumulative Grid Coverage", cov_score],
            ["Reward Hacking Verdict", hacking_verdict],
        ]

        table = Table(table_data, colWidths=[200, 200])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ]
            )
        )
        self._story.append(table)
        self._story.append(Spacer(1, 12))

    def add_summary_section(self) -> None:
        """Add the Gemini-generated natural-language summary."""
        self._story.append(Paragraph("6. Gemini AI Natural Language Explanation", self.h2_style))
        summary_text = self.context.get("llm_summary") or "(No LLM summary generated for this run)"
        # Convert newlines to breaks for ReportLab
        formatted_summary = summary_text.replace("\n", "<br/>")
        self._story.append(Paragraph(formatted_summary, self.body_style))
        self._story.append(Spacer(1, 10))

    def add_recommendations_section(self) -> None:
        """Add actionable recommendations derived from the hacking report."""
        self._story.append(Paragraph("7. Actionable Recommendations & Safety Fixes", self.h2_style))
        report = self.context.get("hacking_report")

        notes = getattr(report, "notes", []) if report else []
        if notes:
            for note in notes:
                self._story.append(Paragraph(f"• {note}", self.bullet_style))
        else:
            self._story.append(
                Paragraph("• Maintain regular coverage tracking and revisit penalty shaping.", self.bullet_style)
            )
            self._story.append(
                Paragraph("• Verify goal state termination logic to prevent infinite exploration loops.", self.bullet_style)
            )

    def generate(self, output_path: Path) -> Path:
        """Render the accumulated story to a PDF file at ``output_path``."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        doc.build(self._story)
        return output_path

