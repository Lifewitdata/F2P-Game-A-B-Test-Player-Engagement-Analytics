-- DuckDB/PostgreSQL window-function query library.

-- Session ordering, recency gap and cumulative engagement.
WITH sequenced AS (
 SELECT player_id,session_id,session_start,session_length_sec,rounds_played,
        ROW_NUMBER() OVER(PARTITION BY player_id ORDER BY session_start) AS session_number,
        LAG(session_start) OVER(PARTITION BY player_id ORDER BY session_start) AS prior_session,
        SUM(rounds_played) OVER(PARTITION BY player_id ORDER BY session_start
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_rounds
 FROM sessions
), ranked AS (
 SELECT *,RANK() OVER(PARTITION BY DATE_TRUNC('month',session_start)
                      ORDER BY session_length_sec DESC) AS monthly_length_rank
 FROM sequenced
)
SELECT *,DATE_DIFF('hour',prior_session,session_start) AS hours_since_prior
FROM ranked;

-- Install cohort retention by variant and age day, with prior-day movement.
WITH cohort AS (
 SELECT player_id,install_date,ab_test_variant FROM players
 WHERE acquisition_channel <> 'internal_qa'
), activity AS (
 SELECT DISTINCT c.player_id,c.install_date,c.ab_test_variant,
        DATE_DIFF('day',c.install_date,CAST(s.session_start AS DATE)) AS age_day
 FROM cohort c JOIN sessions s USING(player_id)
), sizes AS (
 SELECT install_date,ab_test_variant,COUNT(*) AS cohort_size
 FROM cohort GROUP BY 1,2
), daily AS (
 SELECT install_date,ab_test_variant,age_day,COUNT(DISTINCT player_id) AS active_players
 FROM activity GROUP BY 1,2,3
)
SELECT d.*,s.cohort_size,d.active_players::DOUBLE/s.cohort_size AS retention,
       LAG(d.active_players::DOUBLE/s.cohort_size) OVER(
         PARTITION BY d.install_date,d.ab_test_variant ORDER BY d.age_day) AS prior_day_retention
FROM daily d JOIN sizes s USING(install_date,ab_test_variant)
ORDER BY install_date,ab_test_variant,age_day;

-- Cumulative player revenue and payer ranking.
WITH daily_revenue AS (
 SELECT p.player_id,p.ab_test_variant,CAST(t.transaction_timestamp AS DATE) AS revenue_date,
        SUM(t.usd_amount) AS revenue
 FROM players p JOIN iap_transactions t USING(player_id)
 WHERE p.acquisition_channel <> 'internal_qa'
 GROUP BY 1,2,3
), lifetime AS (
 SELECT *,SUM(revenue) OVER(PARTITION BY player_id ORDER BY revenue_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS lifetime_revenue,
        ROW_NUMBER() OVER(PARTITION BY player_id ORDER BY revenue_date) AS purchase_day
 FROM daily_revenue
)
SELECT *,RANK() OVER(PARTITION BY ab_test_variant ORDER BY lifetime_revenue DESC) AS variant_revenue_rank
FROM lifetime;

-- Daily active trend with 7-day average and day-over-day LAG.
WITH daily AS (
 SELECT CAST(session_start AS DATE) AS activity_date,COUNT(DISTINCT player_id) AS dau
 FROM sessions GROUP BY 1
)
SELECT *,AVG(dau) OVER(ORDER BY activity_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS dau_7d_avg,
       LAG(dau) OVER(ORDER BY activity_date) AS prior_day_dau
FROM daily ORDER BY activity_date;
