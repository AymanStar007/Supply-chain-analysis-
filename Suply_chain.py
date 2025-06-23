import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from datetime import datetime

# Load the data
df = pd.read_excel("supplaychain.xlsx")

# --- Data Preparation ---
# Ensure date columns are datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Delivery Date"] = pd.to_datetime(df["Delivery Date"])

# Calculate lead time if missing
if "Lead Time (Days)" not in df.columns or df["Lead Time (Days)"].isnull().all():
    df["Lead Time (Days)"] = (df["Delivery Date"] - df["Order Date"]).dt.days

# Clean and standardize column names
df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

# Convert percentages to numeric
df["delivery_performance_%"] = df["delivery_performance_(%)"].replace("%", "").astype(float)# --- Streamlit App Interface ---
st.set_page_config(layout="wide")
st.title("Supply Chain Dashboard")
st.markdown("This dashboard helps monitor supplier performance, lead time, cost, and delivery trends.")

# Sidebar Filters
with st.sidebar:
    st.header("🔍Filters")
    supplier_filter = st.multiselect("Supplier", options=df["supplier_name"].unique(), default=df["supplier_name"].unique())
    product_filter = st.multiselect("Product", options=df["product_name"].unique(), default=df["product_name"].unique())
    date_range = st.date_input("Order Date Range", [df["order_date"].min(), df["order_date"].max()])

# Apply Filters
filtered_df = df[
    (df["supplier_name"].isin(supplier_filter)) &
    (df["product_name"].isin(product_filter)) &
    (df["order_date"] >= pd.to_datetime(date_range[0])) &
    (df["order_date"] <= pd.to_datetime(date_range[1]))
]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Orders", filtered_df["order_id"].nunique())
with col2:
    st.metric("Avg Lead Time (Days)", round(filtered_df["lead_time_(days)"].mean(), 2))
with col3:
    st.metric("Avg Delivery Performance", f"{round(filtered_df['delivery_performance_%'].mean(), 2)}%")
with col4:
    st.metric("Total Cost ($)", f"${filtered_df['cost_($)'].sum():,.2f}")

# --- Charts Section ---
st.subheader(" Performance Trends")

# Lead Time Over Time
fig_lead_time = px.line(
    filtered_df.groupby("order_date")["lead_time_(days)"].mean().reset_index(),
    x="order_date",
    y="lead_time_(days)",
    title="Average Lead Time Over Time"
)
st.plotly_chart(fig_lead_time, use_container_width=True)

# Delivery Performance by Supplier
fig_perf = px.bar(
    filtered_df.groupby("supplier_name")["delivery_performance_%"].mean().sort_values(ascending=False).reset_index(),
    x="supplier_name",
    y="delivery_performance_%",
    color="delivery_performance_%",
    title="Average Delivery Performance by Supplier",
    color_continuous_scale="Greens"
)
st.plotly_chart(fig_perf, use_container_width=True)

# Cost by Shipping Method
fig_shipping = px.pie(
    filtered_df,
    names="shipping_method",
    values="cost_($)",
    title="Cost Distribution by Shipping Method"
)
st.plotly_chart(fig_shipping, use_container_width=True)

# Quantity vs Cost Scatter
fig_scatter = px.scatter(
    filtered_df,
    x="quantity",
    y="cost_($)",
    color="shipping_method",
    size="delivery_performance_%",
    hover_data=["supplier_name", "product_name"],
    title="Quantity vs Cost Colored by Shipping Method"
)
st.plotly_chart(fig_scatter, use_container_width=True)
