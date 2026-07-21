# A/B Test Readout: Bonus Wheel Variance Test

**Prepared for:** Game Economy & Live Ops stakeholders
**Test:** `bonus_wheel_variance_test`
**Duration:** 30-day observation window
**Sample:** 16,946 players (8,511 control / 8,435 treatment, post-QA-cleanup)

---

## What we tested

The jackpot bonus wheel currently pays out small, steady coin rewards
(Variant A / control). We tested a high-variance version (Variant B) that
mostly pays small amounts but occasionally pays a large jackpot — same
expected value, different payout shape.

**Question:** Does the excitement of occasional big wins improve player
retention, or does the mostly-smaller payout experience hurt it?

## What we found

| Metric | Control (A) | Treatment (B) | Difference | Significant? |
|---|---|---|---|---|
| Day 1 retention | 44.1% | 46.9% | **+2.8pp** | Yes (p < 0.001) |
| Day 7 retention | 25.0% | 25.0% | ~0pp | No |
| Day 30 retention | 4.2% | 3.0% | **−1.1pp** | Yes (p < 0.001) |
| ARPU (30-day) | — | — | Not significant | No revenue difference |

The result **reverses direction** over the test window. Variant B looks
like a clear win after one day, converges to a tie by day 7, and ends up
significantly *worse* than control by day 30.

## Why this matters

If this test had been evaluated on a standard one-week check-in — which is
a common cadence — the team would have shipped Variant B on the strength
of a strong Day-1 signal, and only discovered the retention cost weeks
later, after it had already rolled out to 100% of players.

## Recommendation

**Do not ship Variant B.** The short-term engagement lift doesn't hold up,
and there's no revenue upside to offset the long-term retention cost.

**Process recommendation:** For any mechanic that changes payout *variance*
(not just payout amount), require a minimum 30-day hold before a ship
decision. Novelty effects on variance-based rewards appear to fade faster
than the underlying retention cost takes to show up.

## Possible follow-up test

A hybrid variant — high variance for the first 7 days post-install only,
then reverting to steady payouts — could capture the early engagement
boost without the long-run retention cost. Worth a follow-up test if the
team wants to pursue the "big win moment" concept further.

---
*Full analysis, statistical methodology, and code: see `notebooks/02_ab_test_analysis.ipynb`*
