# %% [markdown]
# # 03 — Engagement & Monetization KPIs
# MAU is distinct players within a calendar month. Stickiness is average
# daily DAU divided by same-month MAU; no cross-window denominator mixing.
# %%
from pathlib import Path
import pandas as pd
from src.analytics import monetization_by_day
DATA=Path("../data")
players=pd.read_csv(DATA/"players.csv",parse_dates=["install_date"])
sessions=pd.read_csv(DATA/"sessions.csv",parse_dates=["session_start"])
txns=pd.read_csv(DATA/"iap_transactions.csv",parse_dates=["transaction_timestamp"])
players=players.loc[players.acquisition_channel.ne("internal_qa")]
sessions=sessions.loc[sessions.player_id.isin(players.player_id)].copy()
sessions["date"]=sessions.session_start.dt.date
dau=sessions.groupby("date").player_id.nunique().rename("DAU")
sessions["month"]=sessions.session_start.dt.to_period("M")
mau=sessions.groupby("month").player_id.nunique().rename("MAU")
avg_dau=sessions.groupby("month").apply(
    lambda g:g.groupby(g.session_start.dt.date).player_id.nunique().mean(),
    include_groups=False).rename("average_DAU")
display(pd.concat([avg_dau,mau,(avg_dau/mau).rename("stickiness")],axis=1))
display(monetization_by_day(players,txns))
cohorts=players.assign(install_week=players.install_date.dt.to_period("W"))
events=sessions.merge(cohorts[["player_id","install_date","install_week"]],on="player_id")
events["week_age"]=(events.session_start.dt.normalize()-events.install_date.dt.normalize()).dt.days//7
active=events.drop_duplicates(["player_id","week_age"]).groupby(
    ["install_week","week_age"]).player_id.nunique().unstack()
sizes=cohorts.groupby("install_week").player_id.nunique()
display((active.div(sizes,axis=0)*100).round(1))
