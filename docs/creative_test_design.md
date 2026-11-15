# Creative Test — Bonus Wheel Visual

## Objective
Test whether a jackpot-forward wheel visual increases qualified engagement without harming downstream player quality. Randomize eligible users once, persist assignment and analyze intention-to-treat.

## Required event contract
- Assignment: player_id, experiment_id, creative_variant, assignment_timestamp, country, platform, acquisition_channel.
- Exposure/impression: event_id, player_id, creative_variant, timestamp, placement, viewable.
- Click: event_id, player_id, creative_variant, timestamp, click_target.

## Metrics
Primary: unique CTR = unique exposed players with at least one click / unique exposed players. Secondary: clicks per 1,000 impressions, impressions per exposed player, tutorial completion and D7 retention. Guardrails: D1/D7 retention, payer rate, crash-free sessions, hide/report rate and cost per qualified visit for paid placements.

## Decision protocol
Pre-register baseline CTR, MDE, alpha, power, sample size and fixed readout date. Use two-sided 5% significance and 80% power. Apply Holm correction when comparing multiple creatives. Do not stop early for a favorable CTR; require no material guardrail regression.

`data/creative_exposures.csv` is synthetic instrumentation-shaped demo data, not evidence of a real campaign.
