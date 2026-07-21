-- ============================================================
-- Bingo F2P Game Analytics — Business Query Library (MySQL)
-- 25 queries covering engagement, retention, A/B testing,
-- monetization, and in-game economy health.
-- ============================================================


-- ------------------------------------------------------------
-- SECTION 1: ENGAGEMENT (DAU / MAU / SESSIONS)
-- ------------------------------------------------------------

-- 1. Daily Active Users (DAU) trend
SELECT
    DATE(session_start) AS activity_date,
    COUNT(DISTINCT player_id) AS dau
FROM sessions
GROUP BY DATE(session_start)
ORDER BY activity_date;


-- 2. Monthly Active Users (MAU) by calendar month
SELECT
    DATE_FORMAT(session_start, '%Y-%m') AS activity_month,
    COUNT(DISTINCT player_id) AS mau
FROM sessions
GROUP BY DATE_FORMAT(session_start, '%Y-%m')
ORDER BY activity_month;


-- 3. DAU/MAU stickiness ratio for the most recent month
SELECT
    ROUND(
        (SELECT COUNT(DISTINCT player_id) FROM sessions
         WHERE session_start >= DATE_SUB(CURDATE(), INTERVAL 1 DAY))
        /
        (SELECT COUNT(DISTINCT player_id) FROM sessions
         WHERE session_start >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)),
        4
    ) AS stickiness_ratio;


-- 4. Average session length (minutes) and rounds per session, by platform
SELECT
    p.platform,
    ROUND(AVG(s.session_length_sec) / 60, 2) AS avg_session_length_min,
    ROUND(AVG(s.rounds_played), 2) AS avg_rounds_per_session
FROM sessions s
JOIN players p ON p.player_id = s.player_id
GROUP BY p.platform;


-- 5. Sessions per player distribution (bucketed) — identifies casual vs. core players
SELECT
    CASE
        WHEN session_count BETWEEN 1 AND 2  THEN '1-2 sessions'
        WHEN session_count BETWEEN 3 AND 10 THEN '3-10 sessions'
        WHEN session_count BETWEEN 11 AND 30 THEN '11-30 sessions'
        ELSE '30+ sessions'
    END AS session_bucket,
    COUNT(*) AS player_count
FROM (
    SELECT player_id, COUNT(*) AS session_count
    FROM sessions
    GROUP BY player_id
) t
GROUP BY session_bucket
ORDER BY MIN(session_count);


-- ------------------------------------------------------------
-- SECTION 2: RETENTION
-- ------------------------------------------------------------

-- 6. Day 1 / Day 7 / Day 30 retention (overall, no A/B split)
SELECT
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 1 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 7 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d7_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 30 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d30_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id;


-- 7. Weekly cohort retention (% of install-week cohort still active in each following week)
SELECT
    YEARWEEK(p.install_date) AS install_cohort_week,
    FLOOR(DATEDIFF(s.session_start, p.install_date) / 7) AS week_since_install,
    COUNT(DISTINCT s.player_id) AS active_players,
    (SELECT COUNT(*) FROM players p2 WHERE YEARWEEK(p2.install_date) = YEARWEEK(p.install_date)) AS cohort_size,
    ROUND(COUNT(DISTINCT s.player_id) /
          (SELECT COUNT(*) FROM players p2 WHERE YEARWEEK(p2.install_date) = YEARWEEK(p.install_date)) * 100, 2) AS retention_pct
FROM players p
JOIN sessions s ON s.player_id = p.player_id
WHERE DATEDIFF(s.session_start, p.install_date) BETWEEN 0 AND 28
GROUP BY install_cohort_week, week_since_install
ORDER BY install_cohort_week, week_since_install;


-- 8. Churned players: installed 14+ days ago, no session in the last 14 days
SELECT p.player_id, p.install_date, p.country, p.spend_tier,
       MAX(s.session_start) AS last_active
FROM players p
JOIN sessions s ON s.player_id = p.player_id
WHERE p.install_date <= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
GROUP BY p.player_id, p.install_date, p.country, p.spend_tier
HAVING MAX(s.session_start) < DATE_SUB(CURDATE(), INTERVAL 14 DAY);


-- 9. Retention by acquisition channel (which channel brings the stickiest players?)
SELECT
    p.acquisition_channel,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 7 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d7_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id
WHERE p.acquisition_channel != 'internal_qa'
GROUP BY p.acquisition_channel
ORDER BY d7_retention_pct DESC;


-- 10. Retention by country (top 5 by D7 retention, minimum 200 installs)
SELECT
    p.country,
    COUNT(DISTINCT p.player_id) AS installs,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 7 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d7_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id
WHERE p.acquisition_channel != 'internal_qa'
GROUP BY p.country
HAVING installs >= 200
ORDER BY d7_retention_pct DESC
LIMIT 5;


-- ------------------------------------------------------------
-- SECTION 3: A/B TEST ANALYSIS (bonus_wheel_variance_test)
-- ------------------------------------------------------------

-- 11. Sample Ratio Mismatch check — raw counts by variant (verify ~50/50 split)
SELECT
    ab_test_variant,
    COUNT(*) AS player_count
FROM players
WHERE ab_test_variant IS NOT NULL
GROUP BY ab_test_variant;


-- 12. D1 retention by A/B variant
SELECT
    p.ab_test_variant,
    COUNT(DISTINCT p.player_id) AS installs,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 1 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d1_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id
WHERE p.ab_test_variant IS NOT NULL
GROUP BY p.ab_test_variant;


-- 13. D7 retention by A/B variant
SELECT
    p.ab_test_variant,
    COUNT(DISTINCT p.player_id) AS installs,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 7 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d7_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id
WHERE p.ab_test_variant IS NOT NULL
GROUP BY p.ab_test_variant;


-- 14. D30 retention by A/B variant (the metric that flips the verdict)
SELECT
    p.ab_test_variant,
    COUNT(DISTINCT p.player_id) AS installs,
    ROUND(COUNT(DISTINCT CASE WHEN DATEDIFF(s.session_start, p.install_date) = 30 THEN p.player_id END)
          / COUNT(DISTINCT p.player_id) * 100, 2) AS d30_retention_pct
FROM players p
LEFT JOIN sessions s ON s.player_id = p.player_id
WHERE p.ab_test_variant IS NOT NULL
GROUP BY p.ab_test_variant;


-- 15. Average bonus coins awarded by variant, for jackpot_wheel bonuses specifically
--     (confirms Variant B has higher variance without changing the mean much)
SELECT
    ab_test_variant,
    bonus_type,
    COUNT(*) AS bonus_count,
    ROUND(AVG(coins_awarded), 2) AS avg_coins,
    ROUND(STDDEV(coins_awarded), 2) AS stddev_coins
FROM bonus_events
WHERE bonus_type = 'jackpot_wheel' AND ab_test_variant IS NOT NULL
GROUP BY ab_test_variant, bonus_type;


-- 16. ARPU guardrail check by A/B variant
SELECT
    p.ab_test_variant,
    COUNT(DISTINCT p.player_id) AS installs,
    ROUND(COALESCE(SUM(t.usd_amount), 0) / COUNT(DISTINCT p.player_id), 4) AS arpu
FROM players p
LEFT JOIN iap_transactions t ON t.player_id = p.player_id
WHERE p.ab_test_variant IS NOT NULL
GROUP BY p.ab_test_variant;


-- 17. Sessions per player by A/B variant (engagement volume, not just retention)
SELECT
    p.ab_test_variant,
    ROUND(AVG(session_count), 2) AS avg_sessions_per_player
FROM players p
JOIN (
    SELECT player_id, COUNT(*) AS session_count
    FROM sessions
    GROUP BY player_id
) s ON s.player_id = p.player_id
WHERE p.ab_test_variant IS NOT NULL
GROUP BY p.ab_test_variant;


-- ------------------------------------------------------------
-- SECTION 4: MONETIZATION
-- ------------------------------------------------------------

-- 18. ARPU and ARPPU by spend tier
SELECT
    p.spend_tier,
    COUNT(DISTINCT p.player_id) AS players,
    ROUND(COALESCE(SUM(t.usd_amount), 0) / COUNT(DISTINCT p.player_id), 2) AS arpu,
    ROUND(COALESCE(SUM(t.usd_amount), 0) /
          NULLIF(COUNT(DISTINCT CASE WHEN t.usd_amount > 0 THEN t.player_id END), 0), 2) AS arppu
FROM players p
LEFT JOIN iap_transactions t ON t.player_id = p.player_id
GROUP BY p.spend_tier;


-- 19. Payer conversion rate (overall % of players who have ever made a purchase)
SELECT
    ROUND(COUNT(DISTINCT t.player_id) / COUNT(DISTINCT p.player_id) * 100, 2) AS payer_conversion_pct
FROM players p
LEFT JOIN iap_transactions t ON t.player_id = p.player_id;


-- 20. Revenue by product type
SELECT
    product_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(usd_amount), 2) AS total_revenue,
    ROUND(AVG(usd_amount), 2) AS avg_transaction_value
FROM iap_transactions
GROUP BY product_type
ORDER BY total_revenue DESC;


-- 21. Top 20 spenders (whale identification)
SELECT
    p.player_id,
    p.country,
    p.spend_tier,
    ROUND(SUM(t.usd_amount), 2) AS lifetime_spend,
    COUNT(t.transaction_id) AS total_transactions
FROM players p
JOIN iap_transactions t ON t.player_id = p.player_id
GROUP BY p.player_id, p.country, p.spend_tier
ORDER BY lifetime_spend DESC
LIMIT 20;


-- 22. Days-to-first-purchase (how long after install do payers convert?)
SELECT
    ROUND(AVG(DATEDIFF(first_purchase, p.install_date)), 1) AS avg_days_to_first_purchase
FROM players p
JOIN (
    SELECT player_id, MIN(transaction_timestamp) AS first_purchase
    FROM iap_transactions
    GROUP BY player_id
) fp ON fp.player_id = p.player_id;


-- ------------------------------------------------------------
-- SECTION 5: IN-GAME ECONOMY
-- ------------------------------------------------------------

-- 23. Payout ratio by room type (economy health check — should be < 1.0)
SELECT
    room_type,
    COUNT(*) AS rounds_played,
    SUM(coins_wagered) AS total_wagered,
    SUM(coins_won) AS total_won,
    ROUND(SUM(coins_won) / SUM(coins_wagered), 4) AS payout_ratio
FROM bingo_rounds
GROUP BY room_type
ORDER BY payout_ratio DESC;


-- 24. Win rate by room type
SELECT
    room_type,
    COUNT(*) AS rounds_played,
    SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) AS rounds_won,
    ROUND(SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS win_rate_pct
FROM bingo_rounds
GROUP BY room_type;


-- 25. Data quality check — internal QA accounts polluting session volume
--     (the issue caught in notebook 01; useful as a recurring monitoring query)
SELECT
    p.player_id,
    p.acquisition_channel,
    COUNT(s.session_id) AS session_count,
    ROUND(AVG(s.session_length_sec), 1) AS avg_session_length_sec
FROM players p
JOIN sessions s ON s.player_id = p.player_id
GROUP BY p.player_id, p.acquisition_channel
HAVING session_count > 100 AND avg_session_length_sec < 20
ORDER BY session_count DESC;
