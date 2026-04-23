-- 1) Highest cost campaigns
SELECT campaign_id, ROUND(SUM(cost), 2) AS total_cost
FROM campaign_performance
GROUP BY campaign_id
ORDER BY total_cost DESC;

-- 2) Highest CTR campaigns
SELECT campaign_id, ROUND(AVG(ctr), 4) AS avg_ctr
FROM campaign_performance
GROUP BY campaign_id
ORDER BY avg_ctr DESC;

-- 3) Clicks trend over time
SELECT date, SUM(clicks) AS total_clicks
FROM campaign_performance
GROUP BY date
ORDER BY date ASC;

-- 4) Average CPA across campaigns
SELECT campaign_id, ROUND(AVG(cpa), 2) AS avg_cpa
FROM campaign_performance
GROUP BY campaign_id
ORDER BY avg_cpa ASC;