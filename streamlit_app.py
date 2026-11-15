from pathlib import Path
import pandas as pd
import streamlit as st
from src.analytics import retention_readout,monetization_by_day

st.set_page_config(page_title="F2P Experiment Monitor",layout="wide")
st.title("F2P Game — Experiment & Engagement Monitor")
st.caption("Rebuildable synthetic event data plus committed project inputs.")
data=Path("data")
required=["players.csv","sessions.csv","iap_transactions.csv"]
missing=[f for f in required if not (data/f).exists()]
if missing:
    st.error(f"Missing {missing}. Run python generate_data.py first.")
    st.stop()
players=pd.read_csv(data/"players.csv",parse_dates=["install_date"])
sessions=pd.read_csv(data/"sessions.csv",parse_dates=["session_start"])
txns=pd.read_csv(data/"iap_transactions.csv",parse_dates=["transaction_timestamp"])
creative_path = data / "creative_exposures.csv"
creative = pd.read_csv(creative_path) if creative_path.exists() else pd.DataFrame()
players=players.loc[players.acquisition_channel.ne("internal_qa")]
sessions=sessions.loc[sessions.player_id.isin(players.player_id)].copy()
sessions["date"]=sessions.session_start.dt.date
dau=sessions.groupby("date").player_id.nunique().rename("DAU")
retention,readout=retention_readout(players,sessions)
money=monetization_by_day(players,txns)
a,b,c=st.columns(3)
a.metric("Latest DAU",f"{int(dau.iloc[-1]):,}" if len(dau) else "—")
b.metric("Test players",f"{int(players.ab_test_variant.isin(['A','B']).sum()):,}")
lift=readout.loc[readout.day.eq(30),"lift_pp"]
c.metric("D30 B − A",f"{lift.iloc[0]:+.2f} pp" if len(lift) else "—")
st.subheader("Daily active users"); st.line_chart(dau)
st.subheader("Retention curves"); st.line_chart(retention.pivot(index="day",columns="variant",values="retention"))
st.subheader("Cumulative ARPU by player age day"); st.line_chart(money.pivot(index="day",columns="variant",values="arpu"))
st.subheader("Experiment readout"); st.dataframe(readout,use_container_width=True)
if not creative.empty:
    st.subheader("Creative test — exposure and CTR")
    exposed = creative.loc[creative.exposed.astype(bool)].groupby("creative_variant").agg(
        assigned_players=("player_id","nunique"), impressions=("impressions","sum"), clicks=("clicks","sum")
    )
    exposed["CTR"] = exposed.clicks / exposed.impressions.replace(0, pd.NA)
    st.dataframe(exposed,use_container_width=True)
    st.bar_chart(exposed[["CTR"]])
threshold=st.sidebar.number_input("Alert threshold (pp)",0.0,20.0,1.0,.25)
if len(lift) and lift.iloc[0] < -threshold:
    st.error(f"Retention alert: B is {abs(lift.iloc[0]):.2f}pp below A at D30.")
else:
    st.success("No D30 retention alert at this threshold.")
