"""Application-wide constants shared across pages and modules."""

from __future__ import annotations

from pathlib import Path

# --- Branding ---------------------------------------------------------
APP_NAME = "XRL Studio"
APP_ICON = ":material/psychology:"   # Material Symbol name used as page_icon in st.set_page_config
APP_TAGLINE = "Explainable Reinforcement Learning for Reward Hacking Detection"
APP_VERSION = "0.1.0"

# --- Filesystem ---------------------------------------------------------
# Absolute path to the repository root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Directories for runtime generated grid files, model checkpoints, and episode logs
GENERATED_DIR = ROOT_DIR / "generated"
GENERATED_GRIDS_DIR = GENERATED_DIR / "grids"
GENERATED_MODELS_DIR = GENERATED_DIR / "models"
GENERATED_LOGS_DIR = GENERATED_DIR / "logs"

# Directories for user export artifacts (PNG charts, CSV logs, JSON reports, PDF summaries)
EXPORTS_DIR = ROOT_DIR / "exports"
EXPORTS_PNG_DIR = EXPORTS_DIR / "png"
EXPORTS_CSV_DIR = EXPORTS_DIR / "csv"
EXPORTS_JSON_DIR = EXPORTS_DIR / "json"
EXPORTS_PDF_DIR = EXPORTS_DIR / "pdf"

ASSETS_DIR = ROOT_DIR / "assets"

# List of all directories created at app initialization via utils.config.ensure_runtime_directories()
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
# Canonical order of wizard steps. Pages check prerequisite steps via utils.session_state.require_step()
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
# Standard and boundary grid dimensions for occupancy grid extraction and environment creation
DEFAULT_GRID_ROWS = 20
DEFAULT_GRID_COLS = 20
MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 60

# --- RL action space --------------------------------------------------
# Action space indices (0: UP, 1: DOWN, 2: LEFT, 3: RIGHT) matching GridWorldEnv discrete space
ACTIONS = ["up", "down", "left", "right"]

# --- Explainability dashboard: heatmap and chart catalogs -----------------
# Catalog of supported 2D grid heatmap visualizers in visualization.heatmaps
HEATMAP_TYPES = ["coverage", "reward", "visit_frequency", "exploit", "loop_density"]

# Catalog of supported 1D metric charts in visualization.charts
CHART_TYPES = [
    "reward_vs_episode",
    "episode_length",
    "coverage_progress",
    "exploration_rate",
    "exploit_score",
    "state_visit_distribution",
]
