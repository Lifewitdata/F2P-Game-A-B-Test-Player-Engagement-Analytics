# %% [markdown]
# # 02 — A/B Test Analysis
# Pre-register: primary D30 retention, two-sided alpha 0.05, 80% power,
# absolute MDE 1.14pp, fixed readout after all assignments mature for 30 days.
# D1/D7 are guardrails. No efficacy peeking before the fixed readout;
# safety, SRM and data-quality checks may run continuously.
# %%
from pathlib import Path
import pandas as pd
from src.analytics import retention_readout,srm_check,experiment_design,business_scenarios,segment_retention
DATA=Path("../data")
players=pd.read_csv(DATA/"players.csv",parse_dates=["install_date"])
sessions=pd.read_csv(DATA/"sessions.csv",parse_dates=["session_start"])
txns=pd.read_csv(DATA/"iap_transactions.csv",parse_dates=["transaction_timestamp"])
players=players.loc[players.acquisition_channel.ne("internal_qa")].copy()
sessions=sessions.loc[sessions.player_id.isin(players.player_id)]
print("SRM:",srm_check(players))
print("Sample size:",experiment_design())
retention,readout=retention_readout(players,sessions)
display(readout)
display(business_scenarios(players,txns))
display(segment_retention(players,sessions))
