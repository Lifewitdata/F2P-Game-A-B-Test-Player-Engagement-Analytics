# %% [markdown]
# # 01 — Data QA
# Run `python generate_data.py` before this audit. These are Jupytext-style
# percent-format notebooks and open in VS Code/Jupyter as Python notebooks.
# %%
from pathlib import Path
import pandas as pd
DATA=Path("../data")
players=pd.read_csv(DATA/"players.csv",parse_dates=["install_date"])
sessions=pd.read_csv(DATA/"sessions.csv",parse_dates=["session_start"])
rounds=pd.read_csv(DATA/"bingo_rounds.csv",parse_dates=["round_timestamp"])
assignments=pd.read_csv(DATA/"ab_test_assignments.csv")
for name,frame in {"players":players,"sessions":sessions,"rounds":rounds,"assignments":assignments}.items():
    print(name,frame.shape)
    display(frame.isna().mean().rename("null_rate").to_frame())
assert players.player_id.is_unique and sessions.session_id.is_unique and rounds.round_id.is_unique
assert sessions.session_length_sec.ge(0).all()
assert rounds[["coins_wagered","coins_won"]].ge(0).all().all()
qa=set(players.loc[players.acquisition_channel.eq("internal_qa"),"player_id"])
print(f"QA players: {len(qa):,}; clean players: {players.player_id.nunique()-len(qa):,}")
