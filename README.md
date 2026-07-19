<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=Bingo%20F2P%20Game%20Analytics&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=A%2FB%20Testing%20%7C%20Retention%20Analytics%20%7C%20Player%20Engagement&descAlignY=55&descSize=18" width="100%"/>

<img src="https://readme-typing-svg.demolab.com/svg?font=Fira+Code&weight=500&size=20&duration=3000&pause=800&color=6C63FF&center=true&vCenter=true&width=650&lines=Would+you+have+shipped+this+test+on+Day+1%3F;A+finding+that+reverses+at+Day+30...;SQL+%2B+Python+%2B+Statistics+%2B+Stakeholder+Comms" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-stats-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-notebooks-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![Status](https://img.shields.io/badge/status-complete-success?style=for-the-badge)

</div>

A portfolio project simulating end-to-end analytics for a live-service F2P
bingo-style mobile game: schema design, synthetic data generation, a full
A/B test analysis with proper statistical methodology, and a standard
engagement/monetization KPI suite.

**Built to mirror the day-to-day of a Data Analyst on a mobile game's live
games team** — the kind of analysis behind titles like Bingo Bash, Monopoly
GO, and similar top-grossing F2P titles.

---

## 🔑 Headline finding

An A/B test on the jackpot bonus wheel's payout structure (steady vs.
high-variance rewards) showed a statistically significant **Day-1
retention lift of +2.8pp** for the treatment group — which fully reversed
into a significant **Day-30 retention loss of −1.1pp** by the end of the
30-day observation window.

<div align="center">

| Day | Control (A) | Treatment (B) | Δ | p-value | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **D1** | 44.1% | 46.9% | 🟢 +2.78pp | 0.0003 | Looks like a win |
| **D7** | 25.0% | 25.0% | ⚪ ~0.00pp | 0.9995 | Converged |
| **D30** | 4.2% | 3.0% | 🔴 −1.14pp | 0.00007 | Significantly worse |

</div>

> 💡 **Evaluated on a typical one-week check-in, this test would have shipped.**
> The full 30-day window shows it shouldn't have.

📄 Full stakeholder readout: [`docs/stakeholder_writeup.md`](docs/stakeholder_writeup.md)

<div align="center">
<img src="docs/retention_curve.png" width="80%" alt="Retention curve showing the crossover between variants"/>
</div>

---

## 📑 Table of contents

- [Project structure](#-project-structure)
- [Data model](#️-data-model)
- [What each notebook covers](#-what-each-notebook-covers)
- [Analysis workflow](#-analysis-workflow)
- [Running it locally](#-running-it-locally)
- [Stack](#️-stack)

---

## 📊 Project structure

```
bingo_analytics/
├── generate_data.py              # synthetic data generator (20K players, 60-day window)
├── sql/
│   └── schema.sql                # table definitions
├── data/                         # generated CSVs (gitignored — run generator locally)
│   └── sample_players.csv        # small sample for browsing without running the generator
├── notebooks/
│   ├── 01_data_exploration_and_qa.ipynb   # data audit, catches a real QA-account contamination issue
│   ├── 02_ab_test_analysis.ipynb          # SRM check, retention curves, significance tests, guardrails
│   └── 03_engagement_kpis.ipynb           # DAU/MAU, cohort retention, ARPU/ARPPU, economy health
├── docs/
│   └── stakeholder_writeup.md    # one-page non-technical readout
└── requirements.txt
```

## 🗂️ Data model

```mermaid
erDiagram
    players ||--o{ sessions : has
    players ||--o{ bingo_rounds : plays
    players ||--o{ bonus_events : receives
    players ||--o{ iap_transactions : makes
    players ||--o| ab_test_assignments : assigned
    sessions ||--o{ bingo_rounds : contains

    players {
        int player_id PK
        date install_date
        string country
        string platform
        string acquisition_channel
        string spend_tier
        string ab_test_variant
    }
    sessions {
        bigint session_id PK
        int player_id FK
        datetime session_start
        int session_length_sec
        int rounds_played
    }
    bingo_rounds {
        bigint round_id PK
        bigint session_id FK
        int player_id FK
        string room_type
        boolean won
        int coins_wagered
        int coins_won
    }
    bonus_events {
        bigint bonus_id PK
        int player_id FK
        string bonus_type
        int coins_awarded
    }
    iap_transactions {
        bigint transaction_id PK
        int player_id FK
        string product_type
        decimal usd_amount
    }
    ab_test_assignments {
        int player_id PK
        string test_name
        string variant
        date assignment_date
    }
```

---

## 🔄 Analysis workflow

```mermaid
flowchart LR
    A[generate_data.py] --> B[01 Data QA]
    B -->|clean_player_ids.csv| C[02 A/B Test Analysis]
    B -->|clean_player_ids.csv| D[03 Engagement KPIs]
    C --> E[Stakeholder Writeup]
    D --> F[KPI Dashboard Metrics]

    style A fill:#6C63FF,color:#fff
    style B fill:#FF6B6B,color:#fff
    style C fill:#4ECDC4,color:#fff
    style D fill:#4ECDC4,color:#fff
    style E fill:#FFD93D,color:#000
    style F fill:#FFD93D,color:#000
```

---

## 🔍 What each notebook covers

<details open>
<summary><b>📓 01 — Data Exploration & QA</b></summary>
<br/>

Standard first-pass audit: nulls, dtypes, ranges. Catches a real data
quality issue baked into this dataset — 25 internal QA/test accounts
generating bot-like session volume that would silently distort DAU and
engagement metrics if not filtered out before analysis.

**🚩 Issue found:** ~0.1% of players (internal QA accounts) generated
~2.7% of all sessions, with near-zero session durations — a bot-like
signature. Excluded via a saved `clean_player_ids.csv` that every
downstream notebook joins against.

</details>

<details>
<summary><b>📓 02 — A/B Test Analysis</b> (the core deliverable)</summary>
<br/>

- Sample Ratio Mismatch (SRM) check via chi-square goodness of fit
- Day-1 / Day-7 / Day-30 retention curves by variant
- Two-proportion z-tests with 95% confidence intervals at each checkpoint
- ARPU guardrail check to rule out a revenue trade-off
- A written recommendation and process takeaway for the team

</details>

<details>
<summary><b>📓 03 — Engagement & Monetization KPIs</b></summary>
<br/>

- DAU / MAU and stickiness ratio
- Weekly cohort retention heatmap
- ARPU and ARPPU by spend tier, payer conversion rate
- In-game economy health check (wager vs. payout ratio by room type)

<div align="center">
<img src="docs/cohort_heatmap.png" width="70%" alt="Weekly cohort retention heatmap"/>
</div>

</details>

---

## 🚀 Running it locally

```bash
pip install -r requirements.txt
python generate_data.py          # generates data/*.csv (~85MB total, ~30 sec)
jupyter notebook notebooks/       # run 01 → 02 → 03, in order
```

---

## 🛠️ Stack

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/-pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/-SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557C?style=flat-square)
![SQL](https://img.shields.io/badge/-SQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Jupyter](https://img.shields.io/badge/-Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)

</div>

Statistical methods: chi-square SRM testing, two-proportion z-tests,
confidence intervals, guardrail metric analysis.

<div align="center">
<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

</div>
