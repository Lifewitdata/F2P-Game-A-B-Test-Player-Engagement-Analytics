# Bonus Wheel Variance Test — Pre-registration

**Test ID:** `bonus_wheel_variance_test`  
**Hypothesis:** Variant B's high-variance reward distribution improves D30 retention versus steady-reward control A. Use a two-sided test because harm is also a decision-relevant outcome.  
**Primary metric:** D30 player retention: at least one qualifying session on install day + 30.  
**Guardrails:** D1 retention, D7 retention, cumulative D30 ARPU/LTV, payer conversion, crash-free sessions, coin issuance and room-level payout integrity.  
**Allocation:** Persistent 1:1 player-level randomization, analyzed intention-to-treat. Exclude only pre-defined internal QA accounts.  
**Design parameters:** 4.2% baseline D30 retention; 1.14 percentage-point absolute MDE; two-sided alpha 0.05; 80% power. The normal-approximation calculation requires **4,225 players per arm** (8,450 total); add 10% for invalid identities, giving **4,648 per arm** (9,296 total). The archived experiment sample (8,502 A / 8,422 B) is above this buffered target.  
**Fixed readout date:** **2026-03-02**. The final assigned cohort's index date is 2026-01-30; D30 is observed through 2026-03-01, and the readout is published after that day is complete.  
**Peeking rule:** No efficacy p-values, interval-based winner declarations, or early ship decisions before the fixed readout. SRM, data-quality and safety checks may run continuously. Any safety stop must be documented as a protocol deviation and reported separately.  
**Multiplicity:** Report 95% confidence intervals for D1/D7/D30 and apply Holm step-down correction across all three p-values. D30 remains the single primary endpoint; D1 and D7 are supporting guardrails/diagnostics.  
**SRM:** 50/50 chi-square goodness-of-fit. Investigate assignment or identity-loss issues if p < 0.01 before reading outcomes.  
**Population:** All eligible randomized players on an intention-to-treat basis. No exclusions based on behavior observed after assignment.  
**Readout interpretation:** Segment cuts by country/platform/channel/spend tier are pre-treatment descriptors. Room type is a post-assignment gameplay behavior and is exploratory only; it cannot establish a causal subgroup effect.  
