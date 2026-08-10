"""Shared export helpers for PNG, CSV, JSON, and PDF artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from utils.constants import EXPORTS_CSV_DIR, EXPORTS_JSON_DIR, EXPORTS_PDF_DIR, EXPORTS_PNG_DIR
from utils.file_io import save_json


def export_png(figure: go.Figure, filename: str) -> Path:
    """Export a Plotly figure to PNG under ``exports/png/``."""
    if not filename.endswith(".png"):
        filename = f"{filename}.png"
    path = EXPORTS_PNG_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_image(str(path))
    return path


def export_csv(dataframe: pd.DataFrame, filename: str) -> Path:
    """Export a pandas DataFrame to CSV under ``exports/csv/``."""
    if not filename.endswith(".csv"):
        filename = f"{filename}.csv"
    path = EXPORTS_CSV_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)
    return path


def export_json(data: dict, filename: str) -> Path:
    """Export a dict to JSON under ``exports/json/``."""
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    path = EXPORTS_JSON_DIR / filename
    return save_json(data, path)


def export_pdf(report_bytes: bytes, filename: str) -> Path:
    """Write generated PDF report bytes under ``exports/pdf/``."""
    if not filename.endswith(".pdf"):
        filename = f"{filename}.pdf"
    path = EXPORTS_PDF_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(report_bytes)
    return path

