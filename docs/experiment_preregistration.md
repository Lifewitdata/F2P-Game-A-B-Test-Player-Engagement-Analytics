# Bonus Wheel Variance Test — Pre-registration

**Test ID:** bonus_wheel_variance_test  
**Hypothesis:** Variant B changes D30 retention versus steady-reward control A; the directional business hypothesis is improvement, with a two-sided statistical test.  
**Primary metric:** D30 retention: assigned player has at least one qualifying session on install day + 30.  
**Guardrails:** D1 and D7 retention, D30 cumulative ARPU, payer conversion, crash-free sessions, and coin issuance/payout integrity.  
**Allocation:** Persistent 1:1 player-level randomization; intention-to-treat population. Exclude only pre-defined internal QA accounts.  
**Design parameters:** Two-sided alpha 0.05, 80% power, absolute D30 MDE 1.14pp, baseline 4.2%. See `experiment_design()` for the reproducible normal-approximation sample-size calculation. Add 10% allowance for invalid identities.  
**Fixed readout:** 30 full observation days after the final assigned player's index date. The exact calendar date must be recorded in the experiment tracker before exposure begins.  
**Peeking:** No efficacy p-values or winner declarations before the fixed readout. SRM, data-quality and safety monitoring may run continuously; safety stops are documented and treated as protocol deviations.  
**Multiplicity:** 95% confidence intervals for D1/D7/D30 and Holm step-down correction across their three p-values. D30 is primary; D1/D7 are diagnostics/guardrails.  
**SRM:** 50/50 chi-square goodness-of-fit; investigate if p < 0.01.  
**Limitation:** Only fully matured 30-day cohorts contribute to the confirmatory D30 endpoint.
