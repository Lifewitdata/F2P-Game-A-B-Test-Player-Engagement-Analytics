import pandas as pd
from src.analytics import holm_adjust, retention_readout, srm_check, monetization_by_day


def sample_data():
    players = pd.DataFrame({
        "player_id": [1, 2, 3, 4],
        "install_date": pd.to_datetime(["2026-01-01"] * 4),
        "ab_test_variant": ["A", "A", "B", "B"],
        "country": ["IN", "US", "IN", "US"],
        "platform": ["iOS", "Android", "iOS", "Android"],
        "acquisition_channel": ["organic", "paid_social", "organic", "paid_search"],
        "spend_tier": ["non_payer", "minnow", "non_payer", "dolphin"],
    })
    sessions = pd.DataFrame({
        "player_id": [3, 3],
        "session_start": pd.to_datetime(["2026-01-02", "2026-01-31"]),
    })
    return players, sessions


def test_holm_adjustment_is_bounded_and_monotonic():
    adjusted = holm_adjust([0.01, 0.04, 0.03])
    assert all(0 <= x <= 1 for x in adjusted)
    assert adjusted[0] <= adjusted[2] <= adjusted[1]


def test_retention_readout_includes_intervals_and_adjustment():
    players, sessions = sample_data()
    _, out = retention_readout(players, sessions, days=(1, 30))
    assert {"ci_low_pp", "ci_high_pp", "p_holm"} <= set(out.columns)
    assert out.loc[out.day.eq(1), "lift_pp"].iloc[0] == 50.0


def test_srm_balanced():
    players, _ = sample_data()
    assert srm_check(players)["pass"]


def test_arpu_includes_zero_spenders_and_has_ltv():
    players, _ = sample_data()
    transactions = pd.DataFrame({
        "player_id": [1, 3],
        "transaction_timestamp": pd.to_datetime(["2026-01-02", "2026-01-03"]),
        "usd_amount": [10.0, 20.0],
    })
    out = monetization_by_day(players, transactions, [30])
    assert out.loc[out.variant.eq("A"), "arpu"].iloc[0] == 5.0
    assert "cumulative_ltv" in out.columns


def test_generator_rebuilds_same_events_from_same_seed():
    from generate_data import generate_events, generate_creative_test
    players = pd.DataFrame({
        "player_id": range(1, 11),
        "install_date": pd.to_datetime(["2026-01-01"] * 10),
        "acquisition_channel": ["organic"] * 10,
        "ab_test_variant": ["A"] * 5 + ["B"] * 5,
    })
    first_sessions, first_rounds = generate_events(players, seed=123)
    second_sessions, second_rounds = generate_events(players, seed=123)
    pd.testing.assert_frame_equal(first_sessions, second_sessions)
    pd.testing.assert_frame_equal(first_rounds, second_rounds)
    first_creative = generate_creative_test(players, seed=456)
    second_creative = generate_creative_test(players, seed=456)
    pd.testing.assert_frame_equal(first_creative, second_creative)
    assert {"assigned", "assignment_timestamp", "exposed", "exposure_timestamp",
            "impressions", "clicks", "ctr"} <= set(first_creative.columns)



def test_room_type_segment_contains_lift():
    from src.analytics import segment_retention
    players, sessions = sample_data()
    rounds = pd.DataFrame({
        "player_id": [1, 3, 3],
        "room_type": ["classic", "classic", "jackpot"],
    })
    segments = segment_retention(players, sessions, rounds=rounds)
    room = segments.loc[segments.dimension.eq("room_type")]
    assert set(room.segment) == {"classic", "jackpot"}
    assert "lift_pp" in room.columns
