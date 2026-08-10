# XRL Studio — Implementation Roadmap

This roadmap breaks the remaining work into independent, sequential
phases. Each phase lists its goal, the files it touches, and a
definition of done. Phases are ordered to match the application flow,
so the app becomes usable end-to-end incrementally rather than all at
once.

Convention: every unimplemented function currently raises
`NotImplementedError` and carries a `TODO(<module>)` marker in its
docstring naming the phase that will fill it in. Grep for `TODO(` to
find all open work.

Status legend: `[x]` complete · `[~]` in progress · `[ ]` not started

---

## Phase 0 — Repository Scaffolding

**Status:** `[x]` Complete

**Goal:** A clean, modular, runnable skeleton that any contributor (human
or AI) can extend module-by-module without restructuring.

**Delivered:**
- Full directory structure: `pages/`, `rl/`, `vision/`, `analytics/`, `visualization/`, `reports/`, `benchmarks/`, `utils/`, `assets/`, `generated/`, `exports/`
- `app.py` with `st.navigation`-based routing across all 14 pages
- Every module's public interface (classes, dataclasses, function signatures, docstrings)
- Centralized session-state management (`utils/session_state.py`)
- Mission profiles and reward presets (fully functional, not stubbed)
- `requirements.txt`, `README.md`, this file
- App launches and every page renders without crashing

---

## Phase 1 — Vision Pipeline: Upload → Grid Extraction → Annotation

**Status:** `[x]` Complete

**Goal:** A user can upload a layout image, extract a real occupancy
grid from it with OpenCV, and manually annotate start/goal/obstacle/
hazard cells.

**Files:**
- `vision/image_loader.py` — decodes uploaded bytes via Pillow into a validated RGB `np.ndarray`; raises `ImageLoadError` for unsupported formats, corrupt bytes, or out-of-range dimensions (`MIN_IMAGE_DIMENSION`–`MAX_IMAGE_DIMENSION`)
- `vision/grid_extractor.py` — real OpenCV pipeline: `cv2.cvtColor` (grayscale) → `cv2.GaussianBlur` → `cv2.threshold` (binary, `invert` flips dark/light-as-obstacle) → cell-wise occupancy voting via `np.linspace` cell edges and a configurable `occupancy_vote_threshold`; `visualize_grid` renders an RGB preview, optionally overlaying an `AnnotationState` (start/goal/obstacle/hazard colors)
- `vision/annotation.py` — `AnnotationManager` with real `set_start` / `set_goal` / `toggle_obstacle` / `toggle_hazard` / `validate` (bounds checks, distinct start/goal, obstacle-conflict checks against both the base grid and manual annotations) / `build_annotated_grid` (non-mutating overlay producing a grid with `START`/`GOAL` cell codes applied)
- `pages/5_Upload_Layout.py` — validates the upload via `load_image` before accepting it, surfaces `ImageLoadError` messages inline
- `pages/6_Grid_Extraction.py` — real threshold/invert/grid-size controls, extraction wired to `GridExtractor`, live preview via `visualize_grid`, obstacle-count summary
- `pages/7_Manual_Annotation.py` — interactive coordinate-picker UI for start/goal, toggle buttons for obstacles/hazards, live annotated preview, inline validation errors, Save button disabled until valid

**Definition of done — verified:**
- ✅ Uploading a PNG/JPG produces a validated `np.ndarray`; corrupt bytes and undersized images are rejected with a clear error, not a crash
- ✅ `GridExtractor.extract_occupancy_grid` returns a real `(rows, cols)` grid using `rl.environment` cell codes (`FREE`/`OBSTACLE`) — confirmed against a synthetic test image with a known obstacle region, including the `invert` flag
- ✅ The extracted grid has a visual preview on the Grid Extraction page, and an annotated preview (start/goal/obstacle/hazard colors) on the Manual Annotation page
- ✅ `AnnotationManager.validate()` correctly requires a distinct start/goal and rejects placement on an obstacle (base-grid or manually-marked), and rejects out-of-bounds cells
- ✅ Annotation persists correctly in `st.session_state["annotation"]`; a re-extracted grid clears stale annotation state so it can't reference cells from a different-shaped grid
- ✅ All 40 headless smoke checks (import + full page execution, mocked Streamlit/Gymnasium/Plotly) still pass; a separate real end-to-end script (`load_image` → `extract_occupancy_grid` → `AnnotationManager`) validated against an actual generated PNG passes all 9 assertions

---

## Phase 2 — Benchmark Library Content

**Status:** `[x]` Complete

**Goal:** Each mission has 1–2 ready-made demo layouts for quick exploration without requiring an upload.

**Delivered:**
- `benchmarks/benchmark_library.py` — `BenchmarkLayout.build_grid()` + `build_annotation()` + populated `BENCHMARK_LIBRARY` with 10 hand-designed demo layouts (2 per mission profile)
- `pages/4_Mission_Selection.py` — surfaces benchmark layout counts and names for the chosen mission profile
- `pages/5_Upload_Layout.py` — provides tabs for selecting a pre-built benchmark or uploading a custom layout image; loading a benchmark populates `occupancy_grid` and `annotation` state and marks wizard steps complete

**Definition of done — verified:**
- ✅ Selecting a benchmark populates `occupancy_grid` and `annotation` without visiting the Upload/Extraction/Annotation pages.


---

## Phase 3 — RL Engine: Environment + Q-learning

**Status:** `[ ]` Not started

**Goal:** A working, mission-agnostic tabular Q-learning loop over `GridWorldEnv`.

**Files:**
- `rl/environment.py` — `reset`, `step` (movement, collisions, reward shaping via `RewardConfig`, termination), `render`
- `rl/q_learning.py` — `select_action` (epsilon-greedy), `update` (Bellman update), `train` (episode loop + epsilon decay + logging)
- `rl/training_logger.py` — `export_csv`
- `pages/9_Train_Agent.py` — surface live progress (episode counter, running reward)

**Definition of done:** Clicking "Start Training" on Page 9 runs to completion and populates `st.session_state["training_logs"]` with real per-episode data for every mission profile.

---

## Phase 4 — Behaviour Analytics

**Status:** `[ ]` Not started

**Goal:** Real coverage, loop, reward-concentration, and revisit-frequency signals computed from training logs.

**Files:** `analytics/coverage.py`, `analytics/loop_detection.py`, `analytics/reward_concentration.py`, `analytics/state_revisit.py`

**Definition of done:** Each function returns real, correctly-shaped output against a completed `TrainingLogger`; Page 10's four tabs show real numbers/tables instead of "not implemented" notices.

---

## Phase 5 — Reward Hacking Detection Aggregation

**Status:** `[ ]` Not started

**Goal:** Combine Phase 4's signals into one interpretable verdict.

**Files:** `analytics/hacking_detector.py` — `detect_reward_hacking` orchestrates all four detectors, sets thresholds for `is_hacking_suspected`, and writes human-readable `notes`.

**Definition of done:** Page 11 shows a real verdict with supporting evidence for at least two clearly-different training runs (one "clean", one deliberately reward-hacked via a skewed `RewardConfig`).

---

## Phase 6 — Visualization: Heatmaps & Charts

**Status:** `[ ]` Not started

**Goal:** Replace placeholder Plotly figures with real, data-driven visualizations.

**Files:** `visualization/heatmaps.py` (5 heatmap types), `visualization/charts.py` (6 chart types)

**Definition of done:** All 5 heatmaps and 6 charts on Page 12 render real data with correct axes/labels/color scales for any completed run.

---

## Phase 7 — Explainability Dashboard: Replay & Policy Inspector

**Status:** `[ ]` Not started

**Goal:** Step-through trajectory replay and the full policy inspector table.

**Files:** `visualization/trajectory_replay.py`, `visualization/policy_inspector.py`, `pages/12_Explainability_Dashboard.py` (wire up the two remaining tabs)

**Definition of done:** Page 12's Trajectory Replay tab lets a user step/scrub through an episode; the Policy Inspector tab shows a sortable/filterable table with all six required columns.

---

## Phase 8 — Gemini LLM Summary

**Status:** `[ ]` Not started

**Goal:** Real Gemini Flash API integration for the natural-language summary.

**Files:** `reports/gemini_summary.py` — implement `generate_summary` using `google-generativeai`, with graceful error handling for missing/invalid keys and API failures.

**Definition of done:** With a valid `GEMINI_API_KEY`, Page 13 generates and displays a real summary grounded in the run's actual metrics.

---

## Phase 9 — PDF Report & Exports

**Status:** `[ ]` Not started

**Goal:** A downloadable PDF covering layout, grid, heatmaps, charts, metrics, Gemini summary, and recommendations, plus PNG/CSV/JSON export.

**Files:** `reports/pdf_generator.py` (all `add_*_section` methods + `generate`), `reports/export_utils.py` (`export_png`, `export_csv`)

**Definition of done:** Page 14 produces a multi-page PDF with all required sections; PNG/CSV/JSON export buttons on the Explainability Dashboard work.

---

## Phase 10 — Polish & Comparison

**Status:** `[ ]` Not started

**Goal:** Production-quality finish for demo/evaluation.

**Scope:**
- Normal vs. Flawed reward comparison view (run two configs, show heatmaps/charts side by side)
- Populate the full benchmark library (all 5 missions)
- Manual QA pass across all 14 pages and all 5 mission profiles
- Performance check on larger grids (up to `MAX_GRID_SIZE`)

**Definition of done:** A full end-to-end run — Home through Download Report — completes cleanly for every mission profile, with no `NotImplementedError` remaining anywhere in the codebase.
