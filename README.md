# Landing Zone EU

A relocation-decision dashboard comparing the Netherlands, Belgium, and
Switzerland on salary, tax burden, cost of living, and electricity price —
built as a fast-follow analyst project on top of the data platform from
[GridPulse EU](https://github.com/Anjum-Kumawat/gridpulse-eu).

**Live dashboard:** _(add your Streamlit Community Cloud URL here once deployed)_

## Why this exists

GridPulse EU proved out a real Azure → Databricks → Snowflake pipeline for
day-ahead electricity prices. Landing Zone EU reuses that same Snowflake
warehouse and asks a more analyst-shaped question: if someone is deciding
between these three countries, how do they actually compare — not just on
energy prices, but on what you'd earn, what you'd keep after tax, and what
things cost?

## Data and sources

Unlike GridPulse EU's daily API ingestion, the salary/tax/cost-of-living
figures here are official annual statistics that don't change day to day, so
this project intentionally skips building a live ingestion pipeline for them.
`sql/setup.sql` loads them as a small static reference table and joins it
against GridPulse EU's live energy price data.

| Metric | Source | Year |
|---|---|---|
| Average annual wage (PPP-adjusted) | OECD Average Annual Wages database | 2024 |
| Tax wedge (single worker, average wage) | OECD Taxing Wages 2025 | 2024 data |
| Comparative price level (EU27=100) | Eurostat Comparative Price Levels of Consumer Goods and Services | 2024 |
| Day-ahead electricity price | ENTSO-E Transparency Platform, via the GridPulse EU pipeline | live |

Deliberately avoided crowd-sourced cost-of-living sites (e.g. Numbeo) in
favor of official government/intergovernmental statistics, so every number
here is independently verifiable.

## What's deliberately deferred

- The reference table is loaded once by hand via `sql/setup.sql`, not
  refreshed automatically — these statistics are published annually, so a
  scheduled pipeline would be overkill for a portfolio project at this scale.
- The dashboard reads from GridPulse EU's personal dbt development schema
  rather than a dedicated production schema/deployment job — reasonable for
  a portfolio build, but a real production setup would promote models to a
  proper deployment target instead.
- The "net purchasing power index" is a derived metric for this analysis
  (after-tax wage adjusted for local price level), not an official statistic
  — documented as such in the dashboard itself.

## Stack

Snowflake (shared with GridPulse EU) → Streamlit Community Cloud.

## Setup

1. Run `sql/setup.sql` once in a Snowsight worksheet against your Snowflake
   account (creates `GRIDPULSE.LANDING_ZONE.COUNTRY_REFERENCE` and the
   `COUNTRY_COMPARISON` view).
2. Deploy `app.py` on Streamlit Community Cloud, pointing at this repo, with
   Snowflake credentials set as secrets (see `app.py` for the expected
   `[snowflake]` keys: `account`, `user`, `password`, `warehouse`,
   `database`, `role`).
