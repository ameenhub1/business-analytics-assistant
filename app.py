
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google import genai
import json
from datetime import datetime, timedelta
import random

# PAGE CONFIG
st.set_page_config(
    page_title="Business Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

# GEMINI CLIENT
GEMINI_API_KEY = "AQ.Ab8RN6JS_diVPc_oxWmGrBzj2PZBMbIuMdgewULD9hcNqHCRqQ"
client = genai.Client(api_key=GEMINI_API_KEY)

# GENERATE DATASET
@st.cache_data
def load_data():
    random.seed(42)
    np.random.seed(42)
    n = 2000
    regions = ["East", "West", "South", "Central"]
    categories = ["Technology", "Furniture", "Office Supplies"]
    segments = ["Consumer", "Corporate", "Home Office"]
    sub_categories = {
        "Technology": ["Phones", "Laptops", "Accessories"],
        "Furniture": ["Chairs", "Tables", "Bookcases"],
        "Office Supplies": ["Paper", "Binders", "Pens"]
    }
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=random.randint(0, 730)) for _ in range(n)]
    data = []
    for i in range(n):
        category = random.choice(categories)
        sub_cat = random.choice(sub_categories[category])
        region = random.choice(regions)
        sales = round(random.uniform(50, 5000), 2)
        discount = round(random.choice([0, 0.1, 0.2, 0.3]), 2)
        profit = round(sales * random.uniform(0.05, 0.35) * (1 - discount), 2)
        if dates[i].month == 3 and dates[i].year == 2023 and region == "South":
            sales = round(sales * 0.4, 2)
            profit = round(profit * 0.3, 2)
        data.append({
            "Order ID": f"ORD-{1000+i}",
            "Order Date": dates[i].strftime("%Y-%m-%d"),
            "Customer Segment": random.choice(segments),
            "Region": region,
            "Category": category,
            "Sub-Category": sub_cat,
            "Sales": sales,
            "Quantity": random.randint(1, 10),
            "Discount": discount,
            "Profit": profit
        })
    df = pd.DataFrame(data)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Year-Month"] = df["Order Date"].dt.strftime("%Y-%m")
    return df

# COMPUTE ANALYTICS
@st.cache_data
def compute_analytics(df):
    total_sales   = df["Sales"].sum()
    total_profit  = df["Profit"].sum()
    total_orders  = df["Order ID"].nunique()
    profit_margin = (total_profit / total_sales) * 100
    avg_order_val = total_sales / total_orders

    category_stats = df.groupby("Category").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count")
    ).round(2)
    category_stats["Margin %"] = (category_stats["Profit"] / category_stats["Revenue"] * 100).round(1)

    region_stats = df.groupby("Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count")
    ).round(2)
    region_stats["Margin %"] = (region_stats["Profit"] / region_stats["Revenue"] * 100).round(1)

    monthly_trend = df.groupby("Year-Month").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).round(2)

    monthly_region = df.groupby(["Year-Month", "Region"])["Sales"].sum().reset_index()
    region_agg = monthly_region.groupby("Region")["Sales"].agg(["mean", "std"]).reset_index()
    monthly_region = monthly_region.merge(region_agg, on="Region")
    monthly_region["is_anomaly"] = (
        monthly_region["Sales"] < (monthly_region["mean"] - 1.5 * monthly_region["std"])
    )
    anomalies = monthly_region[monthly_region["is_anomaly"] == True]

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "profit_margin": profit_margin,
        "avg_order_val": avg_order_val,
        "category_stats": category_stats,
        "region_stats": region_stats,
        "monthly_trend": monthly_trend,
        "monthly_region": monthly_region,
        "anomalies": anomalies
    }

# AI FUNCTION
def ask_ai(question, analytics):
    context = {
        "total_sales": round(analytics["total_sales"], 2),
        "total_profit": round(analytics["total_profit"], 2),
        "profit_margin": round(analytics["profit_margin"], 1),
        "total_orders": analytics["total_orders"],
        "category_performance": analytics["category_stats"].to_dict(),
        "regional_performance": analytics["region_stats"].to_dict(),
        "anomalies_detected": analytics["anomalies"][["Year-Month", "Region", "Sales"]].to_dict(orient="records"),
        "monthly_trend": analytics["monthly_trend"].reset_index().tail(12).to_dict(orient="records")
    }
    prompt = f"""
You are a senior business analyst reviewing sales data.
You have access to the following computed analytics:

{json.dumps(context, indent=2)}

Answer this business question clearly and concisely in 3-5 sentences.
Use specific numbers from the data. Do not make up numbers.

Question: {question}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text

# LOAD DATA
df = load_data()
analytics = compute_analytics(df)

# HEADER
st.title("📊 Business Analytics Assistant")
st.markdown("*AI-powered sales analysis and business insights*")
st.divider()

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Executive Overview",
    "📈 Visual Analytics",
    "⚠️ Anomaly Report",
    "🤖 Ask Your Data"
])

# TAB 1 - EXECUTIVE OVERVIEW
with tab1:
    st.subheader("Executive Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sales",   f"₹{analytics['total_sales']:,.0f}")
    col2.metric("Total Profit",  f"₹{analytics['total_profit']:,.0f}")
    col3.metric("Profit Margin", f"{analytics['profit_margin']:.1f}%")
    col4.metric("Total Orders",  f"{analytics['total_orders']:,}")
    col5.metric("Avg Order Value", f"₹{analytics['avg_order_val']:,.0f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Category Performance")
        st.table(analytics["category_stats"].style.format({'Revenue': '₹{:,.0f}', 'Profit': '₹{:,.0f}', 'Margin %': '{:.1f}%'}))
    with col2:
        st.subheader("Regional Performance")
        st.table(analytics["region_stats"].style.format({'Revenue': '₹{:,.0f}', 'Profit': '₹{:,.0f}', 'Margin %': '{:.1f}%'}))

# TAB 2 - VISUAL ANALYTICS
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.line(
            analytics["monthly_trend"].reset_index(),
            x="Year-Month", y="Sales",
            title="Monthly Sales Trend",
            markers=True,
            color_discrete_sequence=["#2563EB"]
        )
        fig1.update_layout(xaxis_tickangle=-45, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            analytics["category_stats"].reset_index(),
            x="Category", y="Revenue",
            title="Revenue by Category",
            color="Category",
            text="Revenue",
            color_discrete_sequence=["#2563EB", "#16A34A", "#DC2626"]
        )
        fig2.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig3 = px.bar(
            analytics["region_stats"].reset_index(),
            x="Region", y="Revenue",
            title="Revenue by Region",
            color="Margin %",
            text="Revenue",
            color_continuous_scale="RdYlGn"
        )
        fig3.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        segment_stats = df.groupby("Customer Segment")["Sales"].sum().reset_index()
        fig4 = px.pie(
            segment_stats,
            values="Sales",
            names="Customer Segment",
            title="Sales by Customer Segment",
            color_discrete_sequence=["#2563EB", "#16A34A", "#DC2626"]
        )
        st.plotly_chart(fig4, use_container_width=True)

# TAB 3 - ANOMALY REPORT
with tab3:
    st.subheader("⚠️ Anomaly Detection Report")
    anomaly_count = len(analytics["anomalies"])
    st.error(f"{anomaly_count} anomalies detected in sales data")

    st.table(analytics["anomalies"][["Year-Month", "Region", "Sales", "mean"]].rename(columns={"mean": "Expected Sales (Mean)"}).round(2))

    fig5 = px.scatter(
        analytics["monthly_region"],
        x="Year-Month", y="Sales",
        color="Region",
        title="Monthly Sales by Region (X = Anomaly)",
        size_max=12
    )
    anomaly_points = analytics["anomalies"]
    fig5.add_trace(go.Scatter(
        x=anomaly_points["Year-Month"],
        y=anomaly_points["Sales"],
        mode="markers",
        marker=dict(color="red", size=16, symbol="x"),
        name="Anomaly"
    ))
    fig5.update_layout(xaxis_tickangle=-45, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig5, use_container_width=True)

# TAB 4 - ASK YOUR DATA
with tab4:
    st.subheader("🤖 Ask Your Data")

    if st.button("🔍 Generate Business Insights", type="primary"):
        with st.spinner("Analysing your data..."):
            insight = ask_ai(
                "Give me the top 3 business insights with specific numbers and what the business should investigate.",
                analytics
            )
        st.success("Insights Generated")
        st.markdown(insight)

    st.divider()
    st.markdown("**Or ask your own question:**")
    question = st.text_input("Type your question here...",
        placeholder="e.g. Why did sales decline in January 2024?")

    if st.button("Ask", type="secondary") and question:
        with st.spinner("Thinking..."):
            answer = ask_ai(question, analytics)
        st.markdown("**Answer:**")
        st.markdown(answer)

    st.divider()
    st.markdown("**Try these questions:**")
    sample_questions = [
        "Which category generated the most revenue?",
        "Which region has the lowest profit margin?",
        "What anomalies were detected and what do they suggest?",
        "Which customer segment should we focus on?",
        "What should the business investigate urgently?"
    ]
    for q in sample_questions:
        st.markdown(f"- *{q}*")
