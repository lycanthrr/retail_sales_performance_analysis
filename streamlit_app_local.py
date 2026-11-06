# Local version of the Retail Sales dashboard (runs without Snowflake)
# Run with:  streamlit run streamlit_app_local.py

import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retail Sales Dashboard", layout="centered")
st.title("Retail Sales Performance Dashboard")


# === Load data === #
@st.cache_data
def load_data():
    df = pd.read_csv("sales.csv")
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    df = df.rename(columns={"SALES": "TOTAL_SALES"})
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

df = load_data()


# === Metric Functions (pandas versions of the Snowpark code) === #

def get_product_sales_leaderboard(df):
    return (
        df.groupby("PRODUCT", as_index=False)
          .agg(TOTAL_REVENUE=("TOTAL_SALES", "sum"))
          .round(2)
          .sort_values("TOTAL_REVENUE", ascending=False)
    )

def get_regional_sales_comparison(df):
    return (
        df.groupby("REGION", as_index=False)
          .agg(TOTAL_REVENUE=("TOTAL_SALES", "sum"))
          .round(2)
          .sort_values("TOTAL_REVENUE", ascending=False)
    )

def get_monthly_trend_analysis(df):
    monthly = (
        df.assign(SALE_MONTH=df["DATE"].dt.to_period("M").dt.to_timestamp())
          .groupby("SALE_MONTH", as_index=False)
          .agg(TOTAL_REVENUE=("TOTAL_SALES", "sum"))
          .round(2)
          .sort_values("SALE_MONTH")
    )
    monthly["MONTH"] = monthly["SALE_MONTH"].dt.strftime("%b %Y")
    return monthly

def get_units_sold_vs_revenue(df):
    return (
        df.groupby("PRODUCT", as_index=False)
          .agg(TOTAL_UNITS=("UNITS_SOLD", "sum"),
               TOTAL_REVENUE=("TOTAL_SALES", "sum"))
          .round(2)
          .sort_values("PRODUCT")
    )

def revenue_per_unit(df, group_by_column=None):
    if group_by_column:
        out = df.groupby(group_by_column, as_index=False)[["TOTAL_SALES", "UNITS_SOLD"]].sum()
        out["PRICE_PER_UNIT"] = (out["TOTAL_SALES"] / out["UNITS_SOLD"]).round(2)
        return out[[group_by_column, "PRICE_PER_UNIT"]].sort_values("PRICE_PER_UNIT", ascending=False)
    return round(df["TOTAL_SALES"].sum() / df["UNITS_SOLD"].sum(), 2)


# === Chart + table helpers === #

def bar_chart(data, x, y, y_title, money=True, sort="-y"):
    fmt = "$,.0f" if money else ",.0f"
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(f"{x}:N", sort=sort, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y}:Q", title=y_title, scale=alt.Scale(zero=True),
                    axis=alt.Axis(format=fmt)),
            tooltip=[x, alt.Tooltip(y, format=fmt)],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

money_col = st.column_config.NumberColumn(format="$%.2f")
count_col = st.column_config.NumberColumn(format="%d")

def show_table(data, money_cols=(), count_cols=()):
    config = {c: money_col for c in money_cols}
    config.update({c: count_col for c in count_cols})
    st.dataframe(data, hide_index=True, use_container_width=True, column_config=config)


# ======= || Visuals || ======= #

### === Product Sales Leaderboard === ###
st.header("Product Sales Leaderboard")
leaderboard_df = get_product_sales_leaderboard(df)
bar_chart(leaderboard_df, "PRODUCT", "TOTAL_REVENUE", "Total Revenue")
show_table(leaderboard_df, money_cols=["TOTAL_REVENUE"])


### === Regional Sales Comparison === ###
st.header("Regional Sales Comparison")
regional_df = get_regional_sales_comparison(df)
bar_chart(regional_df, "REGION", "TOTAL_REVENUE", "Total Revenue")
show_table(regional_df, money_cols=["TOTAL_REVENUE"])


### === Monthly Trend Analysis === ###
st.header("Monthly Trend Analysis")
monthly_df = get_monthly_trend_analysis(df)
line = (
    alt.Chart(monthly_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("MONTH:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("TOTAL_REVENUE:Q", title="Total Revenue",
                scale=alt.Scale(zero=True), axis=alt.Axis(format="$,.0f")),
        tooltip=["MONTH", alt.Tooltip("TOTAL_REVENUE", format="$,.2f")],
    )
    .properties(height=300)
)
st.altair_chart(line, use_container_width=True)
show_table(monthly_df[["MONTH", "TOTAL_REVENUE"]], money_cols=["TOTAL_REVENUE"])


### === Units Sold vs Revenue === ###
st.header("Units Sold vs Revenue")
units_vs_revenue_df = get_units_sold_vs_revenue(df)

col1, col2 = st.columns(2)
with col1:
    bar_chart(units_vs_revenue_df, "PRODUCT", "TOTAL_UNITS", "Units Sold",
              money=False, sort=None)
with col2:
    bar_chart(units_vs_revenue_df, "PRODUCT", "TOTAL_REVENUE", "Total Revenue",
              sort=None)
show_table(units_vs_revenue_df, money_cols=["TOTAL_REVENUE"], count_cols=["TOTAL_UNITS"])


### === Average Revenue per Unit === ###
st.header("Average Revenue per Unit")
st.metric("Overall Avg Revenue per Unit", f"${revenue_per_unit(df):,.2f}")

col3, col4 = st.columns(2)
with col3:
    st.subheader("By Region")
    rpu_region_df = revenue_per_unit(df, "REGION")
    bar_chart(rpu_region_df, "REGION", "PRICE_PER_UNIT", "Revenue per Unit")
    show_table(rpu_region_df, money_cols=["PRICE_PER_UNIT"])

with col4:
    st.subheader("By Product")
    rpu_product_df = revenue_per_unit(df, "PRODUCT")
    bar_chart(rpu_product_df, "PRODUCT", "PRICE_PER_UNIT", "Revenue per Unit")
    show_table(rpu_product_df, money_cols=["PRICE_PER_UNIT"])
