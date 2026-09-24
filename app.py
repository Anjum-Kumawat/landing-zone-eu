# Landing Zone EU — relocation-decision dashboard
# Compares NL / BE / CH on salary, tax burden, cost of living, and day-ahead
# energy price (the last one reused live from the GridPulse EU project's
# Snowflake data). Reference stats (wages, tax, price level) are official
# annual OECD/Eurostat figures, not something that needs a live pipeline.

import pandas as pd
import plotly.express as px
import snowflake.connector
import streamlit as st

st.set_page_config(page_title="Landing Zone EU", page_icon="🧭", layout="wide")


@st.cache_resource
def get_connection():
    cfg = st.secrets["snowflake"]
    return snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        role=cfg["role"],
    )


@st.cache_data(ttl=3600)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [c[0].lower() for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


st.title("🧭 Landing Zone EU")
st.caption(
    "Comparing the Netherlands, Belgium and Switzerland on salary, tax burden, "
    "cost of living, and day-ahead electricity price — a relocation-decision "
    "reference built on official OECD/Eurostat statistics plus live ENTSO-E "
    "market data (from the companion GridPulse EU project)."
)

df = run_query("select * from LANDING_ZONE.COUNTRY_COMPARISON order by country")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Highest avg wage (PPP)", df.loc[df["avg_annual_wage_ppp_usd"].idxmax(), "country_name"])
with col2:
    st.metric("Lowest tax wedge", df.loc[df["tax_wedge_pct"].idxmin(), "country_name"])
with col3:
    st.metric("Lowest cost of living", df.loc[df["price_level_index"].idxmin(), "country_name"])
with col4:
    st.metric("Highest net purchasing power*", df.loc[df["net_purchasing_power_index"].idxmax(), "country_name"])

st.subheader("Average annual wage (PPP-adjusted, USD)")
st.plotly_chart(
    px.bar(df, x="country_name", y="avg_annual_wage_ppp_usd", color="country_name",
           labels={"country_name": "Country", "avg_annual_wage_ppp_usd": "USD (PPP)"}),
    use_container_width=True,
)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Tax wedge (% of labor cost)")
    st.plotly_chart(
        px.bar(df, x="country_name", y="tax_wedge_pct", color="country_name",
               labels={"country_name": "Country", "tax_wedge_pct": "Tax wedge (%)"}),
        use_container_width=True,
    )
with col_b:
    st.subheader("Cost of living (price level index, EU27=100)")
    st.plotly_chart(
        px.bar(df, x="country_name", y="price_level_index", color="country_name",
               labels={"country_name": "Country", "price_level_index": "Index (EU27=100)"}),
        use_container_width=True,
    )

st.subheader("Day-ahead electricity price (live, from GridPulse EU)")
st.plotly_chart(
    px.bar(df, x="country_name", y="avg_energy_price_eur_mwh", color="country_name",
           labels={"country_name": "Country", "avg_energy_price_eur_mwh": "EUR/MWh"}),
    use_container_width=True,
)

st.subheader("Net purchasing power index*")
st.plotly_chart(
    px.bar(df, x="country_name", y="net_purchasing_power_index", color="country_name",
           labels={"country_name": "Country", "net_purchasing_power_index": "Index"}),
    use_container_width=True,
)
st.caption(
    "*Derived metric, not an official statistic: after-tax wage adjusted for "
    "local price level, indexed for easy comparison. avg_annual_wage_ppp_usd "
    "× (1 − tax_wedge_pct/100) ÷ price_level_index × 100."
)

st.subheader("Full comparison table")
st.dataframe(
    df.rename(columns={
        "country_name": "Country", "avg_annual_wage_ppp_usd": "Avg annual wage (PPP, USD)",
        "avg_monthly_wage_usd": "Avg monthly wage (USD)", "tax_wedge_pct": "Tax wedge (%)",
        "price_level_index": "Price level index", "avg_energy_price_eur_mwh": "Avg energy price (EUR/MWh)",
        "net_purchasing_power_index": "Net purchasing power index*",
    })[["Country", "Avg annual wage (PPP, USD)", "Avg monthly wage (USD)", "Tax wedge (%)",
        "Price level index", "Avg energy price (EUR/MWh)", "Net purchasing power index*"]],
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Sources: OECD Average Annual Wages database (2024); OECD Taxing Wages 2025 "
    "(2024 data, single worker at average wage, no children); Eurostat Comparative "
    "Price Levels of Consumer Goods and Services (2024, EU27=100); ENTSO-E "
    "Transparency Platform via the GridPulse EU pipeline (live)."
)
