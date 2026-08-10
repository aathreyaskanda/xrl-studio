# 🧠 XRL Studio

**Explainable Reinforcement Learning System for Reward Hacking Detection**

XRL Studio trains a tabular Q-learning agent on a grid-world version of a
real-world mission — warehouse inspection, hospital delivery, indoor
security patrol, industrial facility inspection, or search & rescue — and
then explains *what the agent actually learned*, including whether it
found a shortcut that games its reward function instead of solving the
task as intended.

Mission profiles only change **labels and reward presets**. The
underlying grid-world environment and Q-learning engine are identical
across every mission, which makes behaviour directly comparable.

---

## Features

- **Learning module** — a short primer on reward hacking and what XRL Studio looks for
- **Benchmark library** — ready-made layouts per mission for quick demos
- **Image upload + OpenCV occupancy grid extraction** — turn a layout image into a navigable grid
- **GridWorld generation** — a Gymnasium-compatible environment shared by all missions
- **Tabular Q-learning** — with configurable hyperparameters
- **Behaviour logging** — full per-episode trajectory capture
- **Reward hacking detection** — coverage analysis, loop detection, reward concentration, state revisit analysis
- **Explainability dashboard** — heatmaps, trajectory replay, policy inspector, charts
- **Normal vs. flawed comparison** *(planned, Phase 10)*
- **Gemini-generated natural-language summary**
- **PDF report** with export to PNG / CSV / JSON / PDF

## Heatmaps

Coverage · Reward · Visit Frequency · Exploit · Loop Density

## Charts

Reward vs Episode · Episode Length · Coverage Progress · Exploration Rate · Exploit Score · State Visit Distribution

## Policy Inspector

Coordinates · Visit Count · Reward · Q-values · Best Action · Policy Direction

## Report Contents

Layout · Grid · Heatmaps · Charts · Metrics · Gemini Summary · Recommendations

---

## Tech Stack

| Layer | Tools |
|---|---|
| App framework | Streamlit |
| RL environment | Gymnasium, NumPy |
| Computer vision | OpenCV, Pillow |
| Analytics | NumPy, pandas |
| Visualization | Plotly, Matplotlib |
| Reporting | ReportLab, Kaleido (Plotly → PNG) |
| LLM summary | Gemini Flash API |

No React. No FastAPI. No database. No authentication — this is a
single-process Streamlit app, intentionally scoped for a B.Tech major
project.

---

## Project Structure

```
xrl-studio/
├── app.py                     # Entry point: navigation, theming, session init
├── requirements.txt
├── README.md
├── PROJECT_PLAN.md            # Phase-by-phase implementation roadmap
├── .streamlit/
│   ├── config.toml            # Theme
│   └── secrets.toml.example   # Copy to secrets.toml, add GEMINI_API_KEY
│
├── pages/                     # One Streamlit page per step of the guided flow
│   ├── 1_Home.py
│   ├── 2_Learn.py
│   ├── 3_New_Analysis.py
│   ├── 4_Mission_Selection.py
│   ├── 5_Upload_Layout.py
│   ├── 6_Grid_Extraction.py
│   ├── 7_Manual_Annotation.py
│   ├── 8_Reward_Configuration.py
│   ├── 9_Train_Agent.py
│   ├── 10_Behaviour_Analysis.py
│   ├── 11_Reward_Hacking_Detection.py
│   ├── 12_Explainability_Dashboard.py
│   ├── 13_LLM_Summary.py
│   └── 14_Download_Report.py
│
├── rl/                        # Mission-agnostic RL engine
│   ├── environment.py         # GridWorldEnv (Gymnasium)
│   ├── q_learning.py          # QLearningAgent
│   ├── reward_presets.py      # RewardConfig + per-mission presets
│   └── training_logger.py     # EpisodeLog / TrainingLogger
│
├── vision/                    # Image → occupancy grid pipeline
│   ├── image_loader.py
│   ├── grid_extractor.py      # OpenCV grid extraction
│   └── annotation.py          # Start/goal/obstacle/hazard annotation
│
├── analytics/                 # Reward-hacking signal detectors
│   ├── coverage.py
│   ├── loop_detection.py
│   ├── reward_concentration.py
│   ├── state_revisit.py
│   └── hacking_detector.py    # Aggregates the above into one report
│
├── visualization/             # Plotly heatmaps/charts, replay, policy table
│   ├── heatmaps.py
│   ├── charts.py
│   ├── trajectory_replay.py
│   └── policy_inspector.py
│
├── reports/                   # PDF assembly, Gemini summary, exports
│   ├── pdf_generator.py
│   ├── gemini_summary.py
│   └── export_utils.py
│
├── benchmarks/                # Mission profiles + curated demo layouts
│   ├── mission_profiles.py
│   └── benchmark_library.py
│
├── utils/                     # Cross-cutting helpers
│   ├── constants.py
│   ├── session_state.py       # Single source of truth for st.session_state
│   ├── config.py               # Secrets/env access, runtime directory setup
│   └── file_io.py
│
├── assets/                    # Static assets (images, icons, CSS)
├── generated/                 # Per-run artifacts (grids, models, logs)
└── exports/                   # User-downloadable exports (png/csv/json/pdf)
```

---

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) configure the Gemini API key for the LLM Summary step
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your key

# 4. Run the app
streamlit run app.py
```

The app launches into the guided flow — **Home → Learn → New Analysis →
Mission Selection → Upload Layout → Grid Extraction → Manual Annotation →
Reward Configuration → Train Q-learning → Behaviour Analysis → Reward
Hacking Detection → Explainability Dashboard → LLM Summary → Download
Report**. Later steps are gated behind earlier ones via
`utils/session_state.require_step()`, so the sidebar always reflects
where you can currently go.

---

## Current Status

This repository currently implements the full application skeleton:
navigation, session-state management, page flow, and every module's
public interface. Feature logic is filled in incrementally — see
[`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the phase-by-phase roadmap and
current progress.

Unimplemented functions raise `NotImplementedError` with a `TODO(<module>)`
marker in their docstring pointing to the relevant phase. Pages catch
these and show an in-place "not yet implemented" notice, so the app
always launches and every page always renders, even mid-implementation.

## Continuing Development

- Grep for `TODO(` to find every open task, grouped by module area (`rl`, `vision`, `analytics`, `visualization`, `reports`, `benchmarks`).
- Each module's public functions/classes already have their final signatures — implement the body, don't restructure the interface, so pages keep working unchanged.
- `utils/session_state.py` is the single source of truth for what's stored across pages — add new keys there, not ad hoc in a page.
- `utils/constants.py` centralizes shared config (grid defaults, wizard step order, heatmap/chart catalogs) — extend it rather than hardcoding values in pages.
