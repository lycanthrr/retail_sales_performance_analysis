# Import python packages
import streamlit as st
import os
from snowflake.snowpark import functions as F

# Create a database connection to Snowflake
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

# Title
st.title("Retail Sales Performace Dashboard")

# Table from snowflake
df = session.table("RETAIL_SALES_DB.RAW.SALES")

# === Metric Functions === #

def get_product_sales_leaderboard(df):
    return (
        df.group_by("PRODUCT")
            .agg(F.sum("TOTAL_SALES").alias("TOTAL_REVENUE"))
            .sort(F.col("TOTAL_REVENUE").desc())
    )

def get_regional_sales_comparison(df):
    return (
        df.group_by("REGION")
            .agg(F.round(F.sum("TOTAL_SALES"), 2).alias("TOTAL_REVENUE"))
    )

def get_monthly_trend_analysis(df):
    return (
        df.with_column("SALE_MONTH", F.date_trunc("month", F.col("DATE")))
          .group_by("SALE_MONTH")
          .agg(F.round(F.sum("TOTAL_SALES"), 2).alias("TOTAL_REVENUE"))
          .sort(F.col("SALE_MONTH"))
    )

def get_units_sold_vs_revenue(df):
    return (
        df.group_by("PRODUCT")
          .agg(
              F.sum("UNITS_SOLD").alias("TOTAL_UNITS"),
              F.round(F.sum("TOTAL_SALES"), 2).alias("TOTAL_REVENUE")
          )
    )

def average_order_value(df, group_by_column=None):
    if group_by_column:
        return (
            df.group_by(group_by_column)
              .agg(F.round(F.sum("TOTAL_SALES") / F.sum("UNITS_SOLD"), 2).alias("AOV"))
        )
    return df.agg(F.round(F.sum("TOTAL_SALES") / F.sum("UNITS_SOLD"), 2).alias("AOV"))

# ======= || Visual || ======= #

#### === Product Sales Leaderboard === ###
st.header("Product Sales Leaderboard")
leaderboard_df = get_product_sales_leaderboard(df).to_pandas()
st.bar_chart(data=leaderboard_df, x="PRODUCT", y="TOTAL_REVENUE")
st.dataframe(leaderboard_df, use_container_width=True)


### === Regional Sales Comparison === ###
st.header("Regional Sales Comparison")
regional_df = get_regional_sales_comparison(df).to_pandas()
st.bar_chart(data=regional_df, x="REGION", y="TOTAL_REVENUE")
st.dataframe(regional_df, use_container_width=True)


### === Monthly Trend Analysis === ###
st.header("Monthly Trend Analysis")
monthly_df = get_monthly_trend_analysis(df).to_pandas()
st.line_chart(data=monthly_df, x="SALE_MONTH", y="TOTAL_REVENUE")
st.dataframe(monthly_df, use_container_width=True)



### === Units sold vs Revenue === ###
st.header("Units Sold vs Revenue")
units_vs_revenue_df = get_units_sold_vs_revenue(df).to_pandas()

col1, col2 = st.columns(2)
with col1:
    st.bar_chart(data=units_vs_revenue_df, x="PRODUCT", y="TOTAL_UNITS")
with col2:
    st.bar_chart(data=units_vs_revenue_df, x="PRODUCT", y="TOTAL_REVENUE")

st.dataframe(units_vs_revenue_df, use_container_width=True)


### === Section 5: Average Order Value === ###
st.header("Average Order Value")

overall_aov = average_order_value(df).collect()[0]["AOV"]
st.metric("Overall Average Order Value", f"${overall_aov}")

col3, col4 = st.columns(2)
with col3:
    st.subheader("By Region")
    aov_region_df = average_order_value(df, "REGION").to_pandas()
    st.bar_chart(data=aov_region_df, x="REGION", y="AOV")
    st.dataframe(aov_region_df, use_container_width=True)

with col4:
    st.subheader("By Product")
    aov_product_df = average_order_value(df, "PRODUCT").to_pandas()
    st.bar_chart(data=aov_product_df, x="PRODUCT", y="AOV")
    st.dataframe(aov_product_df, use_container_width=True)