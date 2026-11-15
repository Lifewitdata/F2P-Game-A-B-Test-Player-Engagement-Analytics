"""Reusable A/B test, monetization, and cohort analytics."""
import math
import numpy as np
import pandas as pd
from scipy.stats import norm, chi2


def holm_adjust(p_values):
    """Holm step-down adjusted p-values in the original input order."""
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[idx]))
        adjusted[idx] = running
    return adjusted


def retention_frame(players, sessions):
    cohort = players.loc[players.ab_test_variant.isin(["A", "B"])].copy()
    cohort["install_date"] = pd.to_datetime(cohort.install_date)
    events = sessions.merge(
        cohort[["player_id", "install_date", "ab_test_variant"]], on="player_id", how="inner"
    )
    events["day"] = (
        pd.to_datetime(events.session_start).dt.normalize() -
        events.install_date.dt.normalize()
    ).dt.days
    events = events.loc[events.day.between(0, 30)].drop_duplicates(["player_id", "day"])
    sizes = cohort.groupby("ab_test_variant").player_id.nunique()
    rows = []
    for day in range(31):
        active = set(events.loc[events.day.eq(day), "player_id"])
        for variant in ["A", "B"]:
            group = cohort.loc[cohort.ab_test_variant.eq(variant), "player_id"]
            n = int(sizes.get(variant, 0))
            x = int(group.isin(active).sum())
            rows.append((variant, day, n, x, x / n if n else np.nan))
    return pd.DataFrame(rows, columns=[
        "variant", "day", "players", "active_players", "retention"
    ])


def _two_prop(day, a_n, a_x, b_n, b_x):
    pa, pb = a_x / a_n, b_x / b_n
    pooled = (a_x + b_x) / (a_n + b_n)
    se_pool = math.sqrt(pooled * (1 - pooled) * (1 / a_n + 1 / b_n))
    z = (pb - pa) / se_pool if se_pool else 0
    p = float(2 * norm.sf(abs(z)))
    se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
    lift = pb - pa
    return {
        "day": day, "A_rate": pa, "B_rate": pb,
        "A_active": a_x, "B_active": b_x, "A_n": a_n, "B_n": b_n,
        "lift_pp": 100 * lift,
        "ci_low_pp": 100 * (lift - 1.96 * se),
        "ci_high_pp": 100 * (lift + 1.96 * se),
        "p_value": p,
    }


def retention_readout(players, sessions, days=(1, 7, 30)):
    retention = retention_frame(players, sessions)
    rows = []
    for day in days:
        a = retention.loc[(retention.variant == "A") & (retention.day == day)].iloc[0]
        b = retention.loc[(retention.variant == "B") & (retention.day == day)].iloc[0]
        rows.append(_two_prop(
            day, int(a.players), int(a.active_players), int(b.players), int(b.active_players)
        ))
    result = pd.DataFrame(rows)
    result["p_holm"] = holm_adjust(result.p_value.to_numpy())
    result["significant_holm_05"] = result.p_holm < 0.05
    return retention, result


def srm_check(players):
    counts = players.loc[
        players.ab_test_variant.isin(["A", "B"]), "ab_test_variant"
    ].value_counts()
    observed = np.array([counts.get("A", 0), counts.get("B", 0)])
    if observed.sum() == 0:
        raise ValueError("No assigned A/B players found")
    expected = np.repeat(observed.sum() / 2, 2)
    statistic = float(((observed - expected) ** 2 / expected).sum())
    p_value = float(chi2.sf(statistic, 1))
    return {
        "A": int(observed[0]), "B": int(observed[1]),
        "chi2": statistic, "p_value": p_value, "pass": p_value >= 0.01
    }


def monetization_by_day(players, transactions, days=range(31)):
    """Cumulative D0–D30 IAP ARPU/LTV and payer metrics by experiment variant."""
    cohort = players.loc[
        players.ab_test_variant.isin(["A", "B"]),
        ["player_id", "install_date", "ab_test_variant"]
    ].copy()
    cohort["install_date"] = pd.to_datetime(cohort.install_date)
    tx = transactions.copy()
    tx["transaction_timestamp"] = pd.to_datetime(tx.transaction_timestamp)
    tx = tx.merge(cohort, on="player_id", how="inner")
    tx["day"] = (
        tx.transaction_timestamp.dt.normalize() - tx.install_date.dt.normalize()
    ).dt.days
    tx = tx.loc[tx.day.between(0, 30)]
    rows = []
    for day in days:
        for variant in ["A", "B"]:
            population = cohort.loc[cohort.ab_test_variant.eq(variant)]
            spend = tx.loc[
                (tx.day <= day) & (tx.ab_test_variant == variant)
            ].groupby("player_id").usd_amount.sum()
            n = population.player_id.nunique()
            payers = int(spend.index.nunique())
            revenue = float(spend.sum())
            arpu = revenue / n if n else 0.0
            arppu = revenue / payers if payers else 0.0
            rows.append((
                day, variant, n, revenue, arpu, arpu, arppu, payers,
                payers / n if n else 0.0
            ))
    return pd.DataFrame(rows, columns=[
        "day", "variant", "players", "revenue", "arpu", "cumulative_ltv",
        "arppu", "payers", "payer_rate"
    ])


def segment_retention(
    players, sessions, rounds=None,
    dimensions=("country", "platform", "acquisition_channel", "spend_tier")
):
    cohort = players.loc[players.ab_test_variant.isin(["A", "B"])].copy()
    cohort["install_date"] = pd.to_datetime(cohort.install_date)
    events = sessions.merge(cohort[["player_id", "install_date"]], on="player_id")
    events["day"] = (
        pd.to_datetime(events.session_start).dt.normalize() -
        events.install_date.dt.normalize()
    ).dt.days
    events = events.loc[events.day.isin([1, 7, 30])][["player_id", "day"]].drop_duplicates()
    rows = []
    for dimension in dimensions:
        base = cohort[["player_id", "ab_test_variant", dimension]]
        for (segment, variant), group in base.groupby(
            [dimension, "ab_test_variant"], dropna=False
        ):
            for day in (1, 7, 30):
                active = set(events.loc[events.day.eq(day), "player_id"])
                n = group.player_id.nunique()
                x = int(group.player_id.isin(active).sum())
                rows.append((
                    dimension, str(segment), variant, day, n, x, x / n if n else np.nan
                ))
    # Room type is an exposure/behavioral segment, not a pre-treatment player attribute.
    # These cuts are descriptive and may be post-treatment; do not treat them as causal.
    if rounds is not None:
        room_players = rounds[["player_id", "room_type"]].drop_duplicates()
        room_base = cohort[["player_id", "ab_test_variant"]].merge(
            room_players, on="player_id", how="inner"
        )
        for (room, variant), group in room_base.groupby(
            ["room_type", "ab_test_variant"], dropna=False
        ):
            for day in (1, 7, 30):
                active = set(events.loc[events.day.eq(day), "player_id"])
                n = group.player_id.nunique()
                x = int(group.player_id.isin(active).sum())
                rows.append((
                    "room_type", str(room), variant, day, n, x, x / n if n else np.nan
                ))
    result = pd.DataFrame(rows, columns=[
        "dimension", "segment", "variant", "day", "players", "active_players", "retention"
    ])
    keys = ["dimension", "segment", "day"]
    b = result.loc[result.variant.eq("B")].set_index(keys).retention
    control = result.loc[result.variant.eq("A")].set_index(keys).retention
    lift = ((b - control) * 100).rename("lift_pp")
    return result.merge(lift, left_on=keys, right_index=True, how="left")


def experiment_design(baseline=0.042, mde=0.0114, alpha=0.05, power=0.80):
    """Two-sided equal-allocation two-proportion sample-size approximation."""
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    p1, p2 = baseline, baseline - mde
    p_bar = (p1 + p2) / 2
    n = (
        z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) +
        z_power * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2 / (p1 - p2) ** 2
    return {
        "baseline_d30": baseline, "mde_absolute": mde,
        "alpha": alpha, "power": power,
        "required_per_variant": math.ceil(n),
        "total_required": 2 * math.ceil(n),
    }


def business_scenarios(players, sessions, transactions, hybrid_share=0.35):
    """Compare all options at the same eligible population size.

    D30 revenue at risk is a proxy: lost D30 retained players multiplied by
    observed control 30-day ARPU. The observed ARPU difference is reported
    separately and is not attributed solely to retention.
    """
    _, readout = retention_readout(players, sessions, days=(30,))
    money = monetization_by_day(players, transactions, days=(30,))
    a = money.loc[money.variant.eq("A")].iloc[0]
    b = money.loc[money.variant.eq("B")].iloc[0]
    d30 = readout.iloc[0]
    population = int(a.players + b.players)
    lost_players = max(0, int(round((d30.A_rate - d30.B_rate) * int(d30.B_n))))
    retention_revenue_at_risk = lost_players * float(a.arpu)
    a_revenue = float(a.arpu) * population
    b_revenue = float(b.arpu) * population
    hybrid_revenue = ((1 - hybrid_share) * float(a.arpu) + hybrid_share * float(b.arpu)) * population
    return pd.DataFrame([
        ("Keep A", a_revenue, 0.0),
        ("Ship B", b_revenue, b_revenue - a_revenue),
        (f"Hybrid ({hybrid_share:.0%} B mix)", hybrid_revenue, hybrid_revenue - a_revenue),
    ], columns=["option", "projected_30d_revenue", "vs_all_A_revenue"]).assign(
        d30_players_lost=lost_players,
        d30_retention_revenue_at_risk=retention_revenue_at_risk,
        observed_arpu_a=float(a.arpu),
        observed_arpu_b=float(b.arpu),
        observed_arpu_gap_usd=float(b.arpu-a.arpu),
        observed_revenue_delta_same_population=float(b_revenue-a_revenue),
    )
