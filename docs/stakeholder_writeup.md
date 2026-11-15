# A/B Test Readout: Bonus Wheel Variance Test

**Experiment:** `bonus_wheel_variance_test`  
**Population:** 16,924 eligible players after QA-account exclusion  
**Allocation:** 8,502 control (A) / 8,422 treatment (B)  
**Fixed readout:** 2 March 2026, after all players have completed D30 observation

## Executive decision

**Keep Variant A. Do not ship Variant B as a full rollout.** B wins on D1, is statistically indistinguishable from A at D7, and is significantly worse at D30. The early novelty signal does not justify the observed long-run retention and monetization disadvantages.

## Retention readout

| Metric | Control A | Treatment B | B − A | 95% CI for lift | Raw p | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|---:|
| D1 retention | 44.13% | 46.91% | **+2.78pp** | [+1.28, +4.28]pp | 0.000279 | 0.000558 |
| D7 retention | 24.96% | 24.96% | −0.00pp | [−1.30, +1.30]pp | 0.999531 | 0.999531 |
| D30 retention | 4.16% | 3.03% | **−1.14pp** | [−1.70, −0.58]pp | 0.000073 | 0.000219 |

The Holm correction controls family-wise error across the three checkpoint tests. Both the D1 improvement and D30 regression remain significant at 5%; the D7 result remains a tie.

## Commercial impact

The archived IAP ledger reports approximate 30-day ARPU of **$0.173983 for A** and **$0.161177 for B**. On an equal-sized 8,422-player cohort, this is approximately **$107.85 less observed IAP revenue** for B.

The D30 retention gap corresponds to approximately **96 fewer D30 returners** in B versus the A retention rate. Valuing those players at control 30-day ARPU gives a simple **$16.70 revenue-at-risk proxy**. This proxy assumes each lost D30 returner generates average control-cohort ARPU; it is not causal attribution. The observed ARPU difference is reported separately and may reflect payer mix, purchase timing and other factors.

### Rollout scenarios

Scaled to the same 16,924-player population:

| Option | Projected 30-day IAP revenue | Versus all-A |
|---|---:|---:|
| Keep A | ~$2,944.49 | Baseline |
| Ship B | ~$2,727.76 | −$216.73 |
| Hybrid: 35% B / 65% A | ~$2,868.63 | −$75.86 |

The hybrid is an unvalidated planning scenario. It is not a measured causal result and should only proceed as a new randomized experiment.

## Design and analysis controls

The archived sample exceeds the pre-registered sample-size target: 4,225 per arm for 4.2% baseline D30 retention, 1.14pp MDE, two-sided alpha 0.05 and 80% power; with a 10% invalid-identity buffer the target is 4,648 per arm. The experiment uses an SRM check, intention-to-treat population, D1/D7/payer/ARPU guardrails, a fixed D30 readout and no efficacy peeking before maturity.

## Recommendation and next step

Retain A as the default payout mechanic. A short-lived high-variance experience is worth testing only as a new, adequately powered hybrid arm, with persistent randomized assignment, the same D30 primary metric and pre-registered guardrails.

**Data caveat:** The current repository's missing session/round event files are deterministically rebuilt as synthetic demo events calibrated to these archived retention checkpoint counts. They are not recovered historical logs. The IAP source contains 400 transactions, so all monetary figures are descriptive IAP estimates, not full LTV, profit or a revenue forecast.
