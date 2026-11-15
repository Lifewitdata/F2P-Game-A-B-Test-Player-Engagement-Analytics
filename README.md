# F2P Game A/B Test & Player Engagement Analytics

A reproducible portfolio analytics project for a free-to-play bingo-style mobile game. It covers data QA, experiment design, retention inference, monetization, creative testing, engagement KPIs, SQL analytics and a Streamlit monitoring surface.

> **Data integrity note:** Player, assignment, bonus and IAP input files are committed under `data/`. The original missing `sessions.csv` and `bingo_rounds.csv` event logs are rebuilt by `generate_data.py` with a fixed seed. The rebuilt event-level rows are synthetic demo events calibrated to the archived D1/D7/D30 retention counts in the original notebook; they must not be described as recovered production logs.

## Headline experiment readout

The archived experiment compares a steady-reward wheel (A) with a high-variance reward wheel (B). The original notebook's saved outputs show an early lift that reverses by D30.

| Checkpoint | Control A | Treatment B | B − A | Archived p-value |
|---|---:|---:|---:|---:|
| D1 retention | 44.13% | 46.91% | **+2.78pp** | 0.000279 |
| D7 retention | 24.96% | 24.96% | **~0.00pp** | 0.999531 |
| D30 retention | 4.16% | 3.03% | **−1.14pp** | 0.000073 |

The rebuild preserves these three checkpoint counts so the readout remains repeatable. The shared analytics module adds 95% confidence intervals and Holm correction across D1/D7/D30; D30 is the pre-registered primary endpoint.

### Commercial view (30-day IAP)

The archived analysis reported approximate 30-day ARPU of **$0.174 for A** and **$0.161 for B**. At the B sample size (8,422 players), the ARPU difference corresponds to approximately **$108 less observed IAP revenue** for B versus an equal-sized A cohort. The −1.14pp D30 retention gap corresponds to about **96 fewer D30 returners** in the B cohort. A simple revenue-at-risk proxy values those 96 players at control 30-day ARPU: approximately **$16.70**. This is a proxy, not causal attribution or a full LTV forecast.

Illustrative same-population scenarios for 16,924 assigned players (using the archived ARPU values):

| Option | Projected 30-day IAP revenue | Versus all-A |
|---|---:|---:|
| Keep A | ~$2,944.49 | Baseline |
| Ship B | ~$2,727.76 | **−$216.73** |
| Hybrid: 35% B / 65% A | ~$2,868.63 | **−$75.86** |

The hybrid percentage is a planning assumption, not a randomized result. The purchase ledger contains 400 transactions; results are descriptive and exclude ad revenue, platform fees, taxes, operational costs and revenue beyond the observed 30-day window.

## Project structure

```text
.
├── data/
│   ├── players.csv
│   ├── ab_test_assignments.csv
│   ├── bonus_events.csv
│   ├── clean_player_ids.csv
│   ├── iap_transactions.csv
│   └── sample_players.csv
├── generate_data.py                 # deterministic sessions/rounds/creative event generator
├── src/
│   └── analytics.py                  # retention, Holm, SRM, LTV/ARPU, segmentation, scenarios
├── notebooks/
│   ├── 01_data_qa.ipynb
│   ├── 02_ab_test_analysis.ipynb
│   └── 03_engagement_kpis.ipynb
├── sql/
│   ├── schema.sql
│   ├── analysis_queries.sql
│   └── advanced_analytics.sql        # CTEs, ROW_NUMBER, RANK, LAG, rolling totals/cohorts
├── docs/
│   ├── experiment_preregistration.md
│   ├── creative_test_design.md
│   ├── economics_scenarios.md
│   └── stakeholder_writeup.md
├── tests/
└── streamlit_app.py
```

Generated files (`data/sessions.csv`, `data/bingo_rounds.csv`, and `data/creative_exposures.csv`) are intentionally gitignored and regenerated locally.

## Reproduce from a clean clone

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python generate_data.py
pytest -q
```

Run the three notebooks in order:

```bash
jupyter lab notebooks/
```

Launch the daily monitoring dashboard:

```bash
streamlit run streamlit_app.py
```

For a fast CI smoke test, generate a 500-player sample:

```bash
python generate_data.py --limit-players 500
```

## Experiment design

See [the pre-registration](docs/experiment_preregistration.md). It defines the D30 primary metric, 1.14pp MDE, baseline 4.2%, two-sided alpha 0.05, 80% power, D1/D7/payer-rate/ARPU guardrails, fixed maturity-based readout, an explicit no-efficacy-peeking rule and SRM investigation threshold.

## Creative test

[The creative-test plan](docs/creative_test_design.md) specifies player assignment, actual exposure, impression and click event contracts, CTR, downstream retention and guardrails. The generator creates synthetic instrumentation-shaped demo data only; no real campaign result is claimed.

## SQL analytics

`sql/advanced_analytics.sql` includes reusable CTE/window-function patterns for session sequence numbers, previous-session gaps, cumulative rounds, monthly rankings, cohort retention, revenue accumulation and rolling DAU.

## CI

GitHub Actions installs the project requirements, runs pytest, rebuilds generated event files and validates the outputs on pushes and pull requests.
