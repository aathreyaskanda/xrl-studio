"""Shared export helpers for PNG, CSV, JSON, and PDF artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from utils.constants import EXPORTS_JSON_DIR, EXPORTS_PDF_DIR
from utils.file_io import save_json


def export_png(figure: go.Figure, filename: str) -> Path:
    """Export a Plotly figure to PNG under ``exports/png/``.

    TODO(reports): implement. Requires the ``kaleido`` package for
    server-side Plotly image export (already in requirements.txt).
    """
    raise NotImplementedError("export_png is not yet implemented.")


def export_csv(dataframe: pd.DataFrame, filename: str) -> Path:
    """Export a pandas DataFrame to CSV under ``exports/csv/``.

    TODO(reports): implement.
    """
    raise NotImplementedError("export_csv is not yet implemented.")


def export_json(data: dict, filename: str) -> Path:
    """Export a dict to JSON under ``exports/json/``."""
    path = EXPORTS_JSON_DIR / filename
    return save_json(data, path)


def export_pdf(report_bytes: bytes, filename: str) -> Path:
    """Write generated PDF report bytes under ``exports/pdf/``."""
    path = EXPORTS_PDF_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(report_bytes)
    return path
