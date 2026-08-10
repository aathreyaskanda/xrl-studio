"""Application-wide constants shared across pages and modules."""

from __future__ import annotations

from pathlib import Path

# --- Branding ---------------------------------------------------------
APP_NAME = "XRL Studio"
APP_ICON = "🧠"
APP_TAGLINE = "Explainable Reinforcement Learning for Reward Hacking Detection"
APP_VERSION = "0.1.0"

# --- Filesystem ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

GENERATED_DIR = ROOT_DIR / "generated"
GENERATED_GRIDS_DIR = GENERATED_DIR / "grids"
GENERATED_MODELS_DIR = GENERATED_DIR / "models"
GENERATED_LOGS_DIR = GENERATED_DIR / "logs"

EXPORTS_DIR = ROOT_DIR / "exports"
EXPORTS_PNG_DIR = EXPORTS_DIR / "png"
EXPORTS_CSV_DIR = EXPORTS_DIR / "csv"
EXPORTS_JSON_DIR = EXPORTS_DIR / "json"
EXPORTS_PDF_DIR = EXPORTS_DIR / "pdf"

ASSETS_DIR = ROOT_DIR / "assets"

# Every runtime directory that must exist before the app can write to it.
RUNTIME_DIRS = [
    GENERATED_GRIDS_DIR,
    GENERATED_MODELS_DIR,
    GENERATED_LOGS_DIR,
    EXPORTS_PNG_DIR,
    EXPORTS_CSV_DIR,
    EXPORTS_JSON_DIR,
    EXPORTS_PDF_DIR,
]

# --- Guided analysis flow -----------------------------------------------
# Canonical order of the wizard. Pages use this to validate that
# prerequisite steps were completed before rendering their content.
# See utils/session_state.py: require_step() / mark_step_complete().
WIZARD_STEPS = [
    "mission_selection",
    "upload_layout",
    "grid_extraction",
    "manual_annotation",
    "reward_configuration",
    "training",
    "behaviour_analysis",
    "hacking_detection",
    "explainability_dashboard",
    "llm_summary",
    "download_report",
]

# --- Grid defaults --------------------------------------------------------
DEFAULT_GRID_ROWS = 20
DEFAULT_GRID_COLS = 20
MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 60

# --- RL action space --------------------------------------------------
# Index order must match rl.environment.GridWorldEnv's action encoding.
ACTIONS = ["up", "down", "left", "right"]

# --- Explainability dashboard: heatmap and chart catalogs -----------------
HEATMAP_TYPES = ["coverage", "reward", "visit_frequency", "exploit", "loop_density"]

CHART_TYPES = [
    "reward_vs_episode",
    "episode_length",
    "coverage_progress",
    "exploration_rate",
    "exploit_score",
    "state_visit_distribution",
]
