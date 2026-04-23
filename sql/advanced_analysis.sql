-- Advanced SQL portfolio queries for senior analyst interview demos

-- 1) Week-over-week click growth per campaign (CTEs + LAG + CASE)
WITH daily_clicks AS (
    SELECT
        campaign_id,
        date,
        clicks,
        CAST(strftime('%Y', date) AS INTEGER) AS year_num,
        CAST(strftime('%W', date) AS INTEGER) AS week_num
    FROM campaign_performance
),
weekly_clicks AS (
    SELECT
        campaign_id,
        year_num,
        week_num,
        SUM(clicks) AS week_clicks
    FROM daily_clicks
    GROUP BY campaign_id, year_num, week_num
),
wow AS (
    SELECT
        campaign_id,
        year_num,
        week_num,
        week_clicks,
        LAG(week_clicks) OVER (
            PARTITION BY campaign_id
            ORDER BY year_num, week_num
        ) AS previous_week_clicks
    FROM weekly_clicks
)
SELECT
    campaign_id,
    year_num,
    week_num,
    week_clicks,
    previous_week_clicks,
    CASE
        WHEN previous_week_clicks IS NULL OR previous_week_clicks = 0 THEN NULL
        ELSE ROUND(100.0 * (week_clicks - previous_week_clicks) / previous_week_clicks, 2)
    END AS wow_click_growth_pct
FROM wow
ORDER BY campaign_id, year_num, week_num;

-- 2) Rolling 7-day average CTR by campaign (window frame)
WITH daily_ctr AS (
    SELECT
        campaign_id,
        date,
        SUM(clicks) AS total_clicks,
        SUM(impressions) AS total_impressions,
        CASE
            WHEN SUM(impressions) = 0 THEN 0
            ELSE 1.0 * SUM(clicks) / SUM(impressions)
        END AS daily_ctr
    FROM campaign_performance
    GROUP BY campaign_id, date
)
SELECT
    campaign_id,
    date,
    ROUND(daily_ctr, 6) AS daily_ctr,
    ROUND(
        AVG(daily_ctr) OVER (
            PARTITION BY campaign_id
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        6
    ) AS rolling_7d_avg_ctr
FROM daily_ctr
ORDER BY campaign_id, date;

-- 3) Campaign performance ranking by month (CTE + RANK)
WITH monthly_performance AS (
    SELECT
        campaign_id,
        CAST(strftime('%Y', date) AS INTEGER) AS year_num,
        CAST(strftime('%m', date) AS INTEGER) AS month_num,
        SUM(cost) AS total_cost,
        SUM(conversions) AS total_conversions,
        CASE
            WHEN SUM(conversions) = 0 THEN NULL
            ELSE SUM(cost) * 1.0 / SUM(conversions)
        END AS monthly_cpa
    FROM campaign_performance
    GROUP BY campaign_id, year_num, month_num
)
SELECT
    campaign_id,
    year_num,
    month_num,
    ROUND(total_cost, 2) AS total_cost,
    total_conversions,
    ROUND(monthly_cpa, 2) AS monthly_cpa,
    RANK() OVER (
        PARTITION BY year_num, month_num
        ORDER BY monthly_cpa ASC
    ) AS cpa_rank_in_month
FROM monthly_performance
ORDER BY year_num, month_num, cpa_rank_in_month, campaign_id;

-- 4) Cost efficiency tiers using CASE and subquery benchmark
WITH campaign_efficiency AS (
    SELECT
        campaign_id,
        SUM(cost) AS total_cost,
        SUM(conversions) AS total_conversions,
        CASE
            WHEN SUM(conversions) = 0 THEN NULL
            ELSE SUM(cost) * 1.0 / SUM(conversions)
        END AS campaign_cpa
    FROM campaign_performance
    GROUP BY campaign_id
)
SELECT
    ce.campaign_id,
    ROUND(ce.total_cost, 2) AS total_cost,
    ce.total_conversions,
    ROUND(ce.campaign_cpa, 2) AS campaign_cpa,
    CASE
        WHEN ce.campaign_cpa <= (SELECT AVG(cpa) FROM campaign_performance) * 0.85 THEN 'Highly Efficient'
        WHEN ce.campaign_cpa <= (SELECT AVG(cpa) FROM campaign_performance) * 1.10 THEN 'Moderately Efficient'
        ELSE 'Needs Optimization'
    END AS efficiency_tier
FROM campaign_efficiency ce
ORDER BY campaign_cpa ASC;

-- 5) Cumulative spend over time by campaign (running sum window)
WITH daily_spend AS (
    SELECT
        campaign_id,
        date,
        SUM(cost) AS daily_cost
    FROM campaign_performance
    GROUP BY campaign_id, date
)
SELECT
    campaign_id,
    date,
    ROUND(daily_cost, 2) AS daily_cost,
    ROUND(
        SUM(daily_cost) OVER (
            PARTITION BY campaign_id
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS running_total_spend
FROM daily_spend
ORDER BY campaign_id, date;