-- 1) Highest spend campaigns with spend-share (CTE + window)
WITH campaign_spend AS (
    SELECT campaign_id, SUM(cost) AS total_cost
    FROM campaign_performance
    GROUP BY campaign_id
),
spend_ranked AS (
    SELECT
        campaign_id,
        ROUND(total_cost, 2) AS total_cost,
        ROUND(100.0 * total_cost / SUM(total_cost) OVER (), 2) AS spend_share_pct,
        RANK() OVER (ORDER BY total_cost DESC) AS spend_rank
    FROM campaign_spend
)
SELECT campaign_id, total_cost, spend_share_pct, spend_rank
FROM spend_ranked
ORDER BY spend_rank;

-- 2) Highest CTR campaigns with rank (CTE + window)
WITH campaign_ctr AS (
    SELECT campaign_id, AVG(ctr) AS avg_ctr
    FROM campaign_performance
    GROUP BY campaign_id
)
SELECT
    campaign_id,
    ROUND(avg_ctr, 4) AS avg_ctr,
    RANK() OVER (ORDER BY avg_ctr DESC) AS ctr_rank
FROM campaign_ctr
ORDER BY ctr_rank;

-- 3) Click trend with day-over-day deltas (CTE + LAG)
WITH daily_clicks AS (
    SELECT date, SUM(clicks) AS total_clicks
    FROM campaign_performance
    GROUP BY date
)
SELECT
    date,
    total_clicks,
    total_clicks - LAG(total_clicks, 1) OVER (ORDER BY date) AS clicks_delta_vs_prev_day
FROM daily_clicks
ORDER BY date ASC;

-- 4) Average CPA across campaigns plus portfolio benchmark (CTE + window average)
WITH campaign_cpa AS (
    SELECT campaign_id, AVG(cpa) AS avg_cpa
    FROM campaign_performance
    GROUP BY campaign_id
)
SELECT
    campaign_id,
    ROUND(avg_cpa, 2) AS avg_cpa,
    ROUND(AVG(avg_cpa) OVER (), 2) AS portfolio_avg_cpa
FROM campaign_cpa
ORDER BY avg_cpa ASC;