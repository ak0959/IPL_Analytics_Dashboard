# IPL Strategy Dashboard — Data Contract (processed_new)

This document is the single source of truth for:

- What files exist in `data/processed_new/`
- What each file contains (rows, columns)
- What it is used for in Streamlit tabs
- What should NOT be computed at runtime
- How each tab maps to a “data contract”
- Technical conventions: relative paths, Git workflow, Streamlit Cloud behavior

---

## 1) Golden Rule: Runtime Strategy

### ✅ Always use these for Streamlit runtime
- Precomputed KPI CSVs in `data/processed_new/`
- Small masters (match/venue/team dimension tables)

### ❌ Avoid heavy recompute at runtime
- No full-table groupby on `master2_balls_baseline` unless it is a drill-down view
- KPI generation should happen in notebooks/scripts, not inside Streamlit pages

### ✅ Preferred storage format
- Use `.parquet` for heavy masters where available
- Keep CSV available for portability when needed (but Parquet is preferred for speed)

---

## 2) Folder: `data/processed_new/`

All paths in the repo must remain **relative**.

Example load path:
- `data/processed_new/master2_balls_baseline.parquet`

---

## 3) Masters (Foundation Tables)

### A) `master1_matches_baseline.csv`
**Purpose:** Match-level lightweight dimension table (venue + season metadata)  
**Rows:** 1169  
**Columns (6):**
- match_id
- season
- match_date
- venue
- city
- venue_region

**Used for:**
- Tab 1 (filters/context only)
- Tab 3 (venue intelligence context)
- Building match-level grouping keys when needed

**Notes:**
- This file does NOT contain toss information, winner, result, margins, etc.
- It is safe to load fully at runtime.

---

### B) `master2_balls_baseline.csv`
**Purpose:** Ball-by-ball master fact table (single source of truth)  
**Rows:** 278205  
**Columns:** 33 (see schema section)

**Used for:**
- Foundation for KPI generation (batting + bowling + team stats)
- Drill-down analysis when KPI file is not sufficient
- Phase-based analysis using over ranges
- Venue + season filtering (available inside this file)

**Notes:**
- This file is heavy in CSV form.
- Prefer `.parquet` for runtime speed.

---

### B1) `master2_balls_baseline.parquet`
**Purpose:** Optimized storage for the ball-by-ball master  
**Rows:** 278205 (same as CSV)  
**Used for:**
- Fast loading inside Streamlit via `pd.read_parquet`

**Notes:**
- Recommended runtime format
- Requires `pyarrow` (already present in requirements)

---

### C) `master3_teams.csv`
**Purpose:** Team dimension reference  
**Rows:** 16  
**Columns (2):**
- team_id
- team_name

---

### D) `master_team_aliases.csv`
**Purpose:** Team alias mapping (renames + abbreviations + legacy names)  
**Rows:** 46  
**Columns (5):**
- alias_id
- team_id
- alias_name
- canonical_team_name
- team_status

---

### E) `master_teams_ui.csv`
**Purpose:** UI-friendly team lookup (status + display code)  
**Rows:** 16  
**Columns (4):**
- team_id
- team_name
- team_status
- display_code

---

## 4) Config Files

### A) `gates_config.csv`
**Purpose:** Stability thresholds and gating rules for KPIs  
**Rows:** 7  
**Columns (4):**
- metric_area
- scope
- rule
- value

---

### B) `optional_toggles_config.csv`
**Purpose:** Optional strict filters (advanced gating)  
**Rows:** 2  
**Columns (5):**
- toggle_name
- metric_area
- scope
- rule
- value

---

## 5) KPI Outputs (Precomputed CSVs)

All KPI files below are fast-loading and intended for runtime.

---

## 6) Player KPI Files

### 6.1 `kpi_player_batting_alltime.csv`
**Rows:** 202  
**Columns (7):**
- batter
- runs
- balls
- outs
- matches
- strike_rate
- average

---

### 6.2 `kpi_player_batting_season.csv`
**Rows:** 743  
**Columns (8):**
- season_id
- batter
- runs
- balls
- outs
- matches
- strike_rate
- average

---

### 6.3 `kpi_player_bowling_alltime.csv`
**Rows:** 149  
**Columns (9):**
- bowler
- balls
- runs_conceded
- wickets
- matches
- overs
- economy
- strike_rate
- average

---

### 6.4 `kpi_player_bowling_season.csv`
**Rows:** 399  
**Columns (10):**
- season_id
- bowler
- balls
- runs_conceded
- wickets
- matches
- overs
- economy
- strike_rate
- average

---

## 7) Team KPI Files

### 7.1 `kpi_team_batting_alltime.csv`
**Rows:** 14  
**Columns (5):**
- team_batting
- runs
- balls
- matches
- run_rate

---

### 7.2 `kpi_team_batting_season.csv`
**Rows:** 156  
**Columns (6):**
- season_id
- team_batting
- runs
- balls
- matches
- run_rate

---

### 7.3 `kpi_team_bowling_alltime.csv`
**Rows:** 14  
**Columns (8):**
- team_bowling
- balls
- runs_conceded
- wickets
- matches
- overs
- economy
- strike_rate

---

### 7.4 `kpi_team_bowling_season.csv`
**Rows:** 156  
**Columns (9):**
- season_id
- team_bowling
- balls
- runs_conceded
- wickets
- matches
- overs
- economy
- strike_rate

---

## 8) Ball Master Schema (Authoritative)

### `master2_balls_baseline` Columns (33)

- match_id
- batter
- bowler
- non_striker
- team_batting
- team_bowling
- over_number
- ball_number
- batter_runs
- extras
- total_runs
- batsman_type
- bowler_type
- player_out
- fielders_involved
- is_wicket
- is_wide_ball
- is_no_ball
- is_leg_bye
- is_bye
- is_penalty
- wide_ball_runs
- no_ball_runs
- leg_bye_runs
- bye_runs
- penalty_runs
- wicket_kind
- is_super_over
- innings
- season_id
- match_date
- venue
- venue_region

---

## 9) Tab-to-Data Mapping (Source of Truth)

### Tab 0 — Home
**Uses:** No data required

### Tab 1 — All Seasons Quick Insights
**Primary inputs:**
- master2 (prefer parquet)
**Optional:**
- master1

### Tab 2 — Match & Toss Strategy
**Status:** Needs enriched match-level outcomes (missing)

### Tab 3 — Venue Intelligence
**Primary inputs:**
- master1 + master2
- team KPIs

### Tab 4 — Batting Analysis
**Primary inputs:**
- kpi_player_batting_alltime
- kpi_player_batting_season

### Tab 5 — Bowling Analysis
**Primary inputs:**
- kpi_player_bowling_alltime
- kpi_player_bowling_season

---

## 10) Tab KPI Coverage Checklist (What each tab NEEDS)

### ✅ Tab 1 — All Seasons Quick Insights
| KPI / Metric | Source | Columns |
|------------|--------|---------|
| Total matches | master2 | match_id |
| Total balls | master2 | row count |
| Total runs | master2 | total_runs |
| Runs by season | master2 | season_id, total_runs |
| Matches by season | master2 | season_id, match_id |
| Phase splits | master2 | over_number, total_runs |
| Region filter | master2 | venue_region |
| Super over exclusion | master2 | is_super_over |

### ✅ Tab 2 — Match & Toss Strategy
Missing fields:
- toss_winner
- toss_decision
- match_winner
- win margins

### ✅ Tab 3 — Venue Intelligence
| KPI / Metric | Source | Columns |
|------------|--------|---------|
| Venue list | master1 | venue, venue_region |
| Matches per venue | master1 | venue, match_id |
| Avg venue scoring | master2 | venue, innings, total_runs |
| Phase scoring | master2 | venue, over_number, total_runs |
| Team context | team KPI files | run_rate, economy |

### ✅ Tab 4 — Batting Analysis
| KPI / Metric | Source | Columns |
|------------|--------|---------|
| Batting leaders | batting alltime KPI | runs, SR, avg |
| Seasonal leaders | batting season KPI | season_id + batting cols |
| Stability rules | gates_config | batting rules |

### ✅ Tab 5 — Bowling Analysis
| KPI / Metric | Source | Columns |
|------------|--------|---------|
| Bowling leaders | bowling alltime KPI | wickets, econ, SR |
| Seasonal leaders | bowling season KPI | season_id + bowling cols |
| Stability rules | gates_config | bowling rules |

---

## 11) Technical Conventions (Paths, Git, Streamlit Cloud)

### 11.1 Relative path rules (MANDATORY)
All code must use relative paths from the repository root.

✅ Correct examples:
- `Path("data") / "processed_new" / "master1_matches_baseline.csv"`
- `Path("data") / "processed_new" / "master2_balls_baseline.parquet"`

❌ Do NOT use:
- `E:\My Drive\...`
- `C:\Users\...`
- Any absolute OS paths

### 11.2 Where to load files from in Streamlit code
Streamlit pages must load data via `src/data_loader.py`.
Do not hardcode file paths directly in `pages/*.py`.

### 11.3 Git push/pull workflow (simple + safe)
Always do changes locally first, then push.

Recommended commands:

1) Confirm branch + clean state
```bash
git status
