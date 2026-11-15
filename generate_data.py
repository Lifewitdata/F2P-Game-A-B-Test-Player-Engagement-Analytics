"""Deterministic event generator for rebuildable F2P demo data.

The committed player, assignment, bonus, and purchase files remain reference inputs.
This script reconstructs missing session/round event tables and a synthetic
creative-exposure table using a fixed seed. Generated events are demo data.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEED = 20261115


def generate_events(players: pd.DataFrame, seed: int = SEED):
    rng = np.random.default_rng(seed)
    eligible = players.loc[players.acquisition_channel.ne("internal_qa")].copy()
    sessions, rounds = [], []
    session_id = round_id = 1
    rooms = np.array(["classic", "speed", "jackpot"])
    for p in eligible.itertuples(index=False):
        variant = p.ab_test_variant
        n = max(1, int(rng.poisson(11 if variant == "A" else 10.5)))
        active_days = {int(x) for x in rng.integers(0, 31, size=n)}
        active_days.add(1 if rng.random() < (0.46 if variant == "A" else 0.49) else 0)
        if rng.random() < 0.25:
            active_days.add(7)
        if rng.random() < (0.042 if variant == "A" else 0.030):
            active_days.add(30)
        for day in sorted(active_days):
            start = pd.Timestamp(p.install_date) + pd.Timedelta(
                days=day, minutes=int(rng.integers(0, 1440)))
            length = int(np.clip(rng.lognormal(5.9, 0.55), 45, 1800))
            n_rounds = int(rng.integers(1, 9))
            sessions.append((session_id, int(p.player_id), start, length, n_rounds))
            for _ in range(n_rounds):
                wager = int(rng.choice([25, 50, 75, 100, 150]))
                won = bool(rng.random() < 0.18)
                payout = int(wager * rng.uniform(0.6, 2.4)) if won else 0
                rounds.append((round_id, session_id, int(p.player_id),
                               start + pd.Timedelta(minutes=int(rng.integers(0, max(1, length // 60 + 1)))),
                               str(rng.choice(rooms, p=[0.60, 0.30, 0.10])),
                               won, wager, payout))
                round_id += 1
            session_id += 1
    return (
        pd.DataFrame(sessions, columns=["session_id","player_id","session_start","session_length_sec","rounds_played"]),
        pd.DataFrame(rounds, columns=["round_id","session_id","player_id","round_timestamp","room_type","won","coins_wagered","coins_won"])
    )


def generate_creative_test(players: pd.DataFrame, seed: int = SEED + 1):
    rng = np.random.default_rng(seed)
    rows = []
    creatives = ["wheel_visual_control", "wheel_visual_gold_jackpot"]
    for p in players.loc[players.acquisition_channel.ne("internal_qa")].itertuples(index=False):
        assigned = bool(rng.random() < 0.72)
        creative = str(rng.choice(creatives)) if assigned else None
        impressions = int(rng.poisson(3.2)) if assigned else 0
        ctr = 0.085 if creative == creatives[0] else 0.095
        clicks = int(rng.binomial(impressions, ctr)) if impressions else 0
        rows.append((int(p.player_id), creative, assigned, impressions, clicks))
    return pd.DataFrame(rows, columns=["player_id","creative_variant","assigned","impressions","clicks"])


def main():
    parser = argparse.ArgumentParser()
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
    print(f"Generated {len(sessions):,} sessions, {len(rounds):,} rounds, {len(creative):,} creative records")


if __name__ == "__main__":
    main()
