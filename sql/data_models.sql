-- Dimensional model for campaign analytics from campaign_performance (flat table)

DROP TABLE IF EXISTS fact_campaign_daily;
DROP TABLE IF EXISTS dim_campaign;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_channel (
    channel_key INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_name TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_campaign (
    campaign_key INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL UNIQUE,
    channel_key INTEGER NOT NULL,
    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_value TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    week_of_year INTEGER NOT NULL
);

CREATE TABLE fact_campaign_daily (
    fact_key INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key INTEGER NOT NULL,
    campaign_key INTEGER NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    cost REAL NOT NULL,
    conversions INTEGER NOT NULL,
    ctr REAL NOT NULL,
    cpc REAL NOT NULL,
    cpa REAL NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (campaign_key) REFERENCES dim_campaign(campaign_key),
    UNIQUE (date_key, campaign_key)
);

-- Populate dimensions from flat table
INSERT INTO dim_channel (channel_name)
SELECT DISTINCT
    CASE
        WHEN campaign_id LIKE 'Search_%' THEN 'Search'
        WHEN campaign_id LIKE 'Social_%' THEN 'Social'
        WHEN campaign_id LIKE 'Display_%' THEN 'Display'
        WHEN campaign_id LIKE 'Email_%' THEN 'Email'
        ELSE 'Other'
    END AS channel_name
FROM campaign_performance;

INSERT INTO dim_campaign (campaign_id, channel_key)
SELECT
    src.campaign_id,
    dc.channel_key
FROM (
    SELECT DISTINCT
        campaign_id,
        CASE
            WHEN campaign_id LIKE 'Search_%' THEN 'Search'
            WHEN campaign_id LIKE 'Social_%' THEN 'Social'
            WHEN campaign_id LIKE 'Display_%' THEN 'Display'
            WHEN campaign_id LIKE 'Email_%' THEN 'Email'
            ELSE 'Other'
        END AS channel_name
    FROM campaign_performance
) AS src
JOIN dim_channel dc
    ON dc.channel_name = src.channel_name;

INSERT INTO dim_date (date_key, date_value, year, month, day, month_name, week_of_year)
SELECT DISTINCT
    CAST(strftime('%Y%m%d', date) AS INTEGER) AS date_key,
    date AS date_value,
    CAST(strftime('%Y', date) AS INTEGER) AS year,
    CAST(strftime('%m', date) AS INTEGER) AS month,
    CAST(strftime('%d', date) AS INTEGER) AS day,
    CASE strftime('%m', date)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
    END AS month_name,
    CAST(strftime('%W', date) AS INTEGER) AS week_of_year
FROM campaign_performance;

-- Populate fact table at campaign-date grain
INSERT INTO fact_campaign_daily (
    date_key,
    campaign_key,
    impressions,
    clicks,
    cost,
    conversions,
    ctr,
    cpc,
    cpa
)
SELECT
    CAST(strftime('%Y%m%d', cp.date) AS INTEGER) AS date_key,
    dca.campaign_key,
    cp.impressions,
    cp.clicks,
    cp.cost,
    cp.conversions,
    cp.ctr,
    cp.cpc,
    cp.cpa
FROM campaign_performance cp
JOIN dim_campaign dca
    ON cp.campaign_id = dca.campaign_id;

-- Validation view query for star schema joins
SELECT
    dd.date_value,
    dch.channel_name,
    dcp.campaign_id,
    fcd.clicks,
    fcd.cost,
    fcd.cpa
FROM fact_campaign_daily fcd
JOIN dim_date dd ON fcd.date_key = dd.date_key
JOIN dim_campaign dcp ON fcd.campaign_key = dcp.campaign_key
JOIN dim_channel dch ON dcp.channel_key = dch.channel_key
ORDER BY dd.date_value, dcp.campaign_id
LIMIT 20;