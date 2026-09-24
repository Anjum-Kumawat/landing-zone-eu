-- Landing Zone EU — reference data setup
-- Run this once in a Snowsight worksheet against your existing GridPulse
-- Snowflake account. Creates a small static reference table of official
-- salary / tax / cost-of-living statistics for NL, BE, CH, and a comparison
-- view that joins it against the live energy price data already loaded by
-- the GridPulse EU project (GRIDPULSE.DBT_AKUMAWAT.FCT_DAILY_SUMMARY).
--
-- Sources (see README for full citations):
--   Wages:       OECD Average Annual Wages database, 2024
--   Tax wedge:   OECD Taxing Wages 2025 (2024 data), single worker, avg wage, no children
--   Price level: Eurostat Comparative Price Levels of Consumer Goods and Services, 2024 (EU27=100)

CREATE SCHEMA IF NOT EXISTS GRIDPULSE.LANDING_ZONE;

CREATE OR REPLACE TABLE GRIDPULSE.LANDING_ZONE.COUNTRY_REFERENCE (
    country                  STRING,
    country_name              STRING,
    avg_annual_wage_ppp_usd   NUMBER,
    avg_monthly_wage_usd      NUMBER,
    tax_wedge_pct             FLOAT,
    price_level_index         FLOAT,
    wage_source                STRING,
    wage_source_year           INT,
    tax_source                 STRING,
    tax_source_year            INT,
    price_source                STRING,
    price_source_year           INT
);

INSERT INTO GRIDPULSE.LANDING_ZONE.COUNTRY_REFERENCE VALUES
    ('NL', 'Netherlands',  75370, 5251, 35.1, 116, 'OECD Average Annual Wages', 2024, 'OECD Taxing Wages 2025', 2024, 'Eurostat Comparative Price Levels', 2024),
    ('BE', 'Belgium',      76109, 5327, 52.7, 117, 'OECD Average Annual Wages', 2024, 'OECD Taxing Wages 2025', 2024, 'Eurostat Comparative Price Levels', 2024),
    ('CH', 'Switzerland',  87468, 9166, 23.5, 174, 'OECD Average Annual Wages', 2024, 'OECD Taxing Wages 2025', 2024, 'Eurostat Comparative Price Levels', 2024);

-- Net purchasing power index: after-tax wage, adjusted for local price level,
-- indexed so the numbers are easy to compare at a glance (not an official
-- statistic - a derived metric for this analysis, documented as such).
CREATE OR REPLACE VIEW GRIDPULSE.LANDING_ZONE.COUNTRY_COMPARISON AS
SELECT
    r.country,
    r.country_name,
    r.avg_annual_wage_ppp_usd,
    r.avg_monthly_wage_usd,
    r.tax_wedge_pct,
    r.price_level_index,
    e.avg_price_eur_mwh                                                              AS avg_energy_price_eur_mwh,
    ROUND(r.avg_annual_wage_ppp_usd * (1 - r.tax_wedge_pct / 100) / NULLIF(r.price_level_index, 0) * 100, 0) AS net_purchasing_power_index
FROM GRIDPULSE.LANDING_ZONE.COUNTRY_REFERENCE r
LEFT JOIN (
    SELECT country, AVG(avg_price_eur_mwh) AS avg_price_eur_mwh
    FROM GRIDPULSE.DBT_AKUMAWAT.FCT_DAILY_SUMMARY
    GROUP BY country
) e ON e.country = r.country;

SELECT * FROM GRIDPULSE.LANDING_ZONE.COUNTRY_COMPARISON ORDER BY country;
