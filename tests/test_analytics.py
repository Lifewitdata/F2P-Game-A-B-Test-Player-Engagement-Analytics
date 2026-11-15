import pandas as pd
from src.analytics import holm_adjust, retention_readout, srm_check, monetization_by_day


def sample_data():
    players=pd.DataFrame({"player_id":[1,2,3,4],
      "install_date":pd.to_datetime(["2026-01-01"]*4),
      "ab_test_variant":["A","A","B","B"]})
    sessions=pd.DataFrame({"player_id":[1,3,3],
      "session_start":pd.to_datetime(["2026-01-02","2026-01-02","2026-01-31"])})
    return players,sessions


def test_holm_adjustment_is_bounded():
    adjusted=holm_adjust([.01,.04,.03])
    assert all(0<=x<=1 for x in adjusted)
    assert adjusted[0]<=adjusted[2]<=adjusted[1]


def test_retention_readout_includes_intervals_and_adjustment():
    players,sessions=sample_data()
    _,out=retention_readout(players,sessions,days=(1,30))
    assert {"ci_low_pp","ci_high_pp","p_holm"} <= set(out.columns)
    assert out.loc[out.day.eq(1),"lift_pp"].iloc[0] == 50


def test_srm_balanced():
    players,_=sample_data()
    assert srm_check(players)["pass"]


def test_arpu_includes_zero_spenders():
    players,_=sample_data()
    transactions=pd.DataFrame({"player_id":[1,3],
      "transaction_timestamp":pd.to_datetime(["2026-01-02","2026-01-03"]),
      "usd_amount":[10.,20.]})
    out=monetization_by_day(players,transactions,[30])
    assert out.loc[out.variant.eq("A"),"arpu"].iloc[0] == 5
