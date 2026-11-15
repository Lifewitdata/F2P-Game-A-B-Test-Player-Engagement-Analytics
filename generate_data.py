"""Deterministic event generator for reproducible F2P demo data.

The committed player, assignment, bonus and IAP tables remain reference inputs.
Missing session/round events and creative-exposure data are rebuilt with a
fixed seed. Event-level rows are synthetic demo data, not the original raw logs.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEED = 20261115

# Retention counts are calibrated to the archived analysis outputs in the
# original notebook. This reproduces the reported D1/D7/D30 checkpoints.
CHECKPOINT_COUNTS = {
    "A": {1: 3752, 7: 2122, 30: 354},
    "B": {1: 3951, 7: 2102, 30: 255},
}


def generate_events(players: pd.DataFrame, seed: int = SEED):
    rng = np.random.default_rng(seed)
    eligible = players.loc[players.acquisition_channel.ne("internal_qa")].copy()
    selected = {}
    for variant, checkpoints in CHECKPOINT_COUNTS.items():
        ids = eligible.loc[eligible.ab_test_variant.eq(variant), "player_id"].to_numpy()
        selected[variant] = {
            day: set(rng.choice(ids, size=min(count, len(ids)), replace=False).tolist())
            for day, count in checkpoints.items()
        }

    sessions, rounds = [], []
    session_id = round_id = 1
    rooms = np.array(["classic", "speed", "jackpot"])
    for p in eligible.itertuples(index=False):
        variant = p.ab_test_variant
        # Keep the scale close to the notebook's archived event-table volume.
        n_days = min(31, max(1, int(rng.poisson(13.15))))
        active_days = set(rng.choice(np.arange(31), size=n_days, replace=False).tolist())
        if variant in selected:
            for day in (1, 7, 30):
                active_days.discard(day)
                if int(p.player_id) in selected[variant][day]:
                    active_days.add(day)

        for day in sorted(active_days):
            start = pd.Timestamp(p.install_date) + pd.Timedelta(
                days=int(day), minutes=int(rng.integers(0, 1440)))
            length = int(np.clip(rng.lognormal(5.9, 0.55), 45, 1800))
            n_rounds = max(1, min(12, int(rng.poisson(4.9))))
            sessions.append((session_id, int(p.player_id), start, length, n_rounds))
            for _ in range(n_rounds):
                wager = int(rng.choice([25, 50, 75, 100, 150]))
                won = bool(rng.random() < 0.18)
                payout = int(wager * rng.uniform(0.6, 2.4)) if won else 0
                round_minute = int(rng.integers(0, max(1, length // 60 + 1)))
                rounds.append((
                    round_id, session_id, int(p.player_id),
                    start + pd.Timedelta(minutes=round_minute),
                    str(rng.choice(rooms, p=[0.60, 0.30, 0.10])),
                    won, wager, payout
                ))
                round_id += 1
            session_id += 1

    sessions_df = pd.DataFrame(sessions, columns=[
        "session_id", "player_id", "session_start", "session_length_sec", "rounds_played"
    ])
    rounds_df = pd.DataFrame(rounds, columns=[
        "round_id", "session_id", "player_id", "round_timestamp", "room_type",
        "won", "coins_wagered", "coins_won"
    ])
    return sessions_df, rounds_df


def generate_creative_test(players: pd.DataFrame, seed: int = SEED + 1):
    rng = np.random.default_rng(seed)
    rows = []
    creatives = ["wheel_visual_control", "wheel_visual_gold_jackpot"]
    for p in players.loc[players.acquisition_channel.ne("internal_qa")].itertuples(index=False):
        assigned = bool(rng.random() < 0.72)
        creative = str(rng.choice(creatives)) if assigned else None
        exposed = bool(assigned and rng.random() < 0.95)
        impressions = int(rng.poisson(3.2)) if exposed else 0
        ctr = 0.085 if creative == creatives[0] else 0.095
        clicks = int(rng.binomial(impressions, ctr)) if impressions else 0
        observed_ctr = clicks / impressions if impressions else np.nan
        rows.append((int(p.player_id), creative, assigned, exposed,
                     impressions, clicks, observed_ctr))
    return pd.DataFrame(rows, columns=[
        "player_id", "creative_variant", "assigned", "exposed",
        "impressions", "clicks", "ctr"
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    players = pd.read_csv(args.data_dir / "players.csv", parse_dates=["install_date"])
    sessions, rounds = generate_events(players, args.seed)
    creative = generate_creative_test(players, args.seed + 1)
    sessions.to_csv(args.data_dir / "sessions.csv", index=False)
    rounds.to_csv(args.data_dir / "bingo_rounds.csv", index=False)
    creative.to_csv(args.data_dir / "creative_exposures.csv", index=False)
    print(
        f"Generated {len(sessions):,} sessions, {len(rounds):,} rounds and "
        f"{len(creative):,} creative assignments in {args.data_dir}"
    )


if __name__ == "__main__":
    main()
