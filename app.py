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
    page_title="Business Analytics Assistant-BAA",
    page_icon="",
    layout="wide"
)

# ─────────────────────────────────────────────
# PROFESSIONAL UI THEME
# ─────────────────────────────────────────────

st.markdown("""
<style>

    /* Main application background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Main title */
    h1 {
        color: #0F172A;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Section headings */
    h2, h3 {
        color: #0F172A;
        font-weight: 650;
    }
    
    h2, h3 {
    color: #0F172A;
    font-weight: 650;
}

/* Streamlit subheaders */
div[data-testid="stSubheader"] {
    color: #0F172A !important;
}

div[data-testid="stSubheader"] h2 {
    color: #0F172A !important;
    font-weight: 700 !important;
}

.stSubheader,
.stSubheader h2,
.stSubheader h3 {
    color: #0F172A !important;
}

    /* Normal text */
    p, label {
        color: #334155;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
    }

    /* Tab underline */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563EB;
    }

    /* Streamlit metric cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #0F172A;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #CBD5E1;
        padding: 0.55rem 1rem;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: white;
        border: none;
    }

    /* Text input */
    div[data-baseweb="input"] {
        border-radius: 10px;
    }

    /* Dataframes/tables */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Hero Header */
.hero-header {
    background: linear-gradient(135deg, #0F172A, #1E3A8A);
    padding: 28px 32px;
    border-radius: 18px;
    margin-bottom: 24px;
}

.hero-label {
    color: #93C5FD;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.hero-title {
    color: white;
    font-size: 32px;
    font-weight: 750;
    margin-top: 6px;
}

.hero-subtitle {
    color: #CBD5E1;
    font-size: 15px;
    margin-top: 6px;
}

/* Section headings */
div[data-testid="stHeading"] h2,
div[data-testid="stHeading"] h3 {
    color: #0F172A !important;
    font-weight: 700 !important;
}

/* Fallback for Streamlit heading containers */
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 {
    color: #0F172A !important;
    font-weight: 700 !important;
}

/* Navigation tabs */
button[data-baseweb="tab"] {
    color: #334155 !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #1D4ED8 !important;
    font-weight: 700 !important;
}

/* Navigation tabs */
button[data-baseweb="tab"] {
    color: #334155 !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #1D4ED8 !important;
    font-weight: 700 !important;
}

div.questions-title {
    color: #2563EB !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    margin: 20px 0 14px 0;
}

/* Generate Business Insights button */
div.stButton > button[kind="primary"] {
    background-color: #111827 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #000000  !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;

}

</style>
""", unsafe_allow_html=True)

# GEMINI CLIENT
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────
# SMART COLUMN DETECTOR
# ─────────────────────────────────────────────
def detect_columns(df):
    cols = {c.lower().strip(): c for c in df.columns}
    mapping = {}

    for key in ["order date", "date", "order_date", "transaction date", "sale date", "invoice date"]:
        if key in cols:
            mapping["date"] = cols[key]
            break

    for key in ["sales", "revenue", "amount", "total", "sale amount", "gross sales", "net sales"]:
        if key in cols:
            mapping["sales"] = cols[key]
            break

    for key in ["profit", "net profit", "margin", "net income", "earnings", "gross profit"]:
        if key in cols:
            mapping["profit"] = cols[key]
            break

    for key in ["region", "area", "zone", "territory", "location", "state"]:
        if key in cols:
            mapping["region"] = cols[key]
            break

    for key in ["category", "product category", "type", "department", "product type"]:
        if key in cols:
            mapping["category"] = cols[key]
            break

    for key in ["customer segment", "segment", "customer type", "client type"]:
        if key in cols:
            mapping["segment"] = cols[key]
            break

    for key in ["order id", "order_id", "id", "transaction id", "invoice", "invoice no"]:
        if key in cols:
            mapping["order_id"] = cols[key]
            break

    return mapping

# ─────────────────────────────────────────────
# PROCESS UPLOADED CSV
# ─────────────────────────────────────────────
def process_uploaded_data(df, mapping):
    processed = pd.DataFrame()

    if "date" in mapping:
        try:
            processed["Order Date"] = pd.to_datetime(df[mapping["date"]])
        except:
            processed["Order Date"] = pd.date_range("2022-01-01", periods=len(df), freq="D")
    else:
        processed["Order Date"] = pd.date_range("2022-01-01", periods=len(df), freq="D")

    if "sales" in mapping:
        processed["Sales"] = pd.to_numeric(df[mapping["sales"]], errors="coerce").fillna(0)
    else:
        processed["Sales"] = 0

    if "profit" in mapping:
        processed["Profit"] = pd.to_numeric(df[mapping["profit"]], errors="coerce").fillna(0)
    else:
        processed["Profit"] = (processed["Sales"] * 0.15).round(2)

    if "region" in mapping:
        processed["Region"] = df[mapping["region"]].astype(str).str.strip()
    else:
        processed["Region"] = "General"

    if "category" in mapping:
        processed["Category"] = df[mapping["category"]].astype(str).str.strip()
    else:
        processed["Category"] = "General"

    if "segment" in mapping:
        processed["Customer Segment"] = df[mapping["segment"]].astype(str).str.strip()
    else:
        processed["Customer Segment"] = "General"

    if "order_id" in mapping:
        processed["Order ID"] = df[mapping["order_id"]].astype(str)
    else:
        processed["Order ID"] = [f"ORD-{i}" for i in range(len(df))]

    processed["Year"]       = processed["Order Date"].dt.year
    processed["Month"]      = processed["Order Date"].dt.month
    processed["Month Name"] = processed["Order Date"].dt.strftime("%b")
    processed["Year-Month"] = processed["Order Date"].dt.strftime("%Y-%m")

    return processed

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

# ─────────────────────────────────────────────
# SIDEBAR — CSV UPLOAD
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Upload Your Data")
    st.markdown(
        "<p style='color:#64748B; font-size:13px;'>Upload any sales CSV. Columns are auto-detected.</p>",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        """
        <p style='color:#64748B; font-size:12px; font-weight:600;'>SUPPORTED COLUMNS</p>
        <p style='color:#94A3B8; font-size:12px; line-height:1.8;'>
        • Date / Order Date<br>
        • Sales / Revenue / Amount<br>
        • Profit / Margin / Net Profit<br>
        • Region / Area / Zone<br>
        • Category / Type<br>
        • Segment / Customer Type<br>
        • Order ID (optional)
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.markdown(
        "<p style='color:#64748B; font-size:11px; text-align:center;'>Built by Muhammed Ameen M P</p>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# LOAD & PROCESS DATA
# ─────────────────────────────────────────────
data_source = "demo"
mapping = {}

if uploaded_file is not None:
    try:
        raw_df   = pd.read_csv(uploaded_file)
        mapping  = detect_columns(raw_df)
        df       = process_uploaded_data(raw_df, mapping)
        data_source = "uploaded"
    except Exception as e:
        st.warning(f"Could not read file: {e} — falling back to demo data.")
        df = load_data()
else:
    df = load_data()

analytics = compute_analytics(df)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
if data_source == "uploaded":
    subtitle = f"Analysing: <strong>{uploaded_file.name}</strong> — {len(df):,} rows loaded"
    if mapping:
        detected = ", ".join([f"{k} → {v}" for k, v in mapping.items()])
        subtitle += f"<br><span style='font-size:12px; color:#93C5FD;'>Detected: {detected}</span>"
else:
    subtitle = "AI-powered sales analysis, anomaly detection and business insights — <em>using demo dataset</em>"

st.markdown(
    f"""
    <div class="hero-header">
        <div class="hero-label">BUSINESS INTELLIGENCE</div>
        <div class="hero-title">Business Analytics Assistant</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """,
    unsafe_allow_html=True
)

     


# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Overview",
    "Visual Analytics",
    "Anomaly Report",
    "AI ChatBot"
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
          # CATEGORY AND REGIONAL PERFORMANCE
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Category Performance")

        category_display = analytics["category_stats"].copy()
        category_display = category_display.reset_index()
        category_display = category_display.rename(columns={"index": "Category"})

        category_display["Revenue"] = category_display["Revenue"].map(
            lambda x: f"₹{x:,.0f}"
        )

        category_display["Profit"] = category_display["Profit"].map(
            lambda x: f"₹{x:,.0f}"
        )

        category_display["Margin %"] = category_display["Margin %"].map(
            lambda x: f"{x:.1f}%"
        )

        st.dataframe(
            category_display,
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("Regional Performance")

        region_display = analytics["region_stats"].copy()
        region_display = region_display.reset_index()
        region_display = region_display.rename(columns={"index": "Region"})

        region_display["Revenue"] = region_display["Revenue"].map(
            lambda x: f"₹{x:,.0f}"
        )

        region_display["Profit"] = region_display["Profit"].map(
            lambda x: f"₹{x:,.0f}"
        )

        region_display["Margin %"] = region_display["Margin %"].map(
            lambda x: f"{x:.1f}%"
        )

        st.dataframe(
            region_display,
            use_container_width=True,
            hide_index=True
        )
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
        fig1.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",

            font=dict(
                family="Arial",
                color="#334155"
            ),

            title_font=dict(
                size=18,
                color="#0F172A"
            ),

            margin=dict(
                l=70,
                r=20,
                t=60,
                b=70
            ),

            xaxis=dict(
                showgrid=False,
                linecolor="#94A3B8",
                tickangle=-45,

                tickfont=dict(
                    color="#334155",
                    size=12
                ),

                title=dict(
                    text="Year-Month",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),

            yaxis=dict(
                gridcolor="#CBD5E1",
                zeroline=False,

                tickfont=dict(
                    color="#334155",
                    size=12
                ),

                title=dict(
                    text="Sales",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),

            hoverlabel=dict(
                bgcolor="white",
                font_color="#0F172A"
            )
        )
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
        fig2.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="Arial",
                color="#334155"
            ),
            title_font=dict(
                size=18,
                color="#0F172A"
            ),
            margin=dict(
                l=70,
                r=30,
                t=60,
                b=60
            ),
            xaxis=dict(
                showgrid=False,
                linecolor="#94A3B8",
                tickfont=dict(
                    color="#334155",
                    size=12
                ),
                title=dict(
                    text="Category",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),
            yaxis=dict(
                gridcolor="#CBD5E1",
                zeroline=False,
                tickfont=dict(
                    color="#334155",
                    size=12
                ),
                title=dict(
                    text="Revenue",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_color="#0F172A"
            ),
            showlegend=False
        )
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
        fig3.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="Arial",
                color="#334155"
            ),
            title_font=dict(
                size=18,
                color="#0F172A"
            ),
            margin=dict(
                l=70,
                r=30,
                t=60,
                b=60
            ),
            xaxis=dict(
                showgrid=False,
                linecolor="#94A3B8",
                tickfont=dict(
                    color="#334155",
                    size=12
                ),
                title=dict(
                    text="Region",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),
            yaxis=dict(
                gridcolor="#CBD5E1",
                zeroline=False,
                tickfont=dict(
                    color="#334155",
                    size=12
                ),
                title=dict(
                    text="Revenue",
                    font=dict(
                        color="#334155",
                        size=13
                    )
                )
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_color="#0F172A"
            )
        )
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
        fig4.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="Arial",
                color="#334155"
            ),
            title_font=dict(
                size=18,
                color="#0F172A"
            ),
            margin=dict(
                l=30,
                r=30,
                t=60,
                b=30
            ),
            legend=dict(
                font=dict(
                    color="#334155",
                    size=12
                )
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_color="#0F172A"
            )
        )
        st.plotly_chart(fig4, use_container_width=True)

# TAB 3 - ANOMALY REPORT
with tab3:
    st.subheader("Anomaly Detection Report")

    anomaly_count = len(analytics["anomalies"])

    st.error(f"{anomaly_count} anomalies detected in sales data")

    # ANOMALY TABLE
    anomaly_display = analytics["anomalies"][
        ["Year-Month", "Region", "Sales", "mean"]
    ].copy()

    anomaly_display = anomaly_display.rename(
        columns={"mean": "Expected Sales (Mean)"}
    )

    anomaly_display["Sales"] = anomaly_display["Sales"].map(
        lambda x: f"₹{x:,.0f}"
    )

    anomaly_display["Expected Sales (Mean)"] = anomaly_display[
        "Expected Sales (Mean)"
    ].map(
        lambda x: f"₹{x:,.0f}"
    )

    st.dataframe(
        anomaly_display,
        use_container_width=True,
        hide_index=True
    )

    # ANOMALY CHART
    fig5 = px.scatter(
        analytics["monthly_region"],
        x="Year-Month",
        y="Sales",
        color="Region",
        title="Monthly Sales by Region",
        size_max=12
    )

    anomaly_points = analytics["anomalies"]

    fig5.add_trace(
        go.Scatter(
            x=anomaly_points["Year-Month"],
            y=anomaly_points["Sales"],
            mode="markers",
            marker=dict(
                color="#DC2626",
                size=16,
                symbol="x"
            ),
            name="Anomaly"
        )
    )

    fig5.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial",
            color="#334155"
        ),

        title_font=dict(
            size=18,
            color="#0F172A"
        ),

        margin=dict(
            l=70,
            r=30,
            t=60,
            b=70
        ),

        xaxis=dict(
            showgrid=False,
            linecolor="#94A3B8",
            tickangle=-45,

            tickfont=dict(
                color="#334155",
                size=12
            ),

            title=dict(
                text="Year-Month",
                font=dict(
                    color="#334155",
                    size=13
                )
            )
        ),

        yaxis=dict(
            gridcolor="#CBD5E1",
            zeroline=False,

            tickfont=dict(
                color="#334155",
                size=12
            ),

            title=dict(
                text="Sales",
                font=dict(
                    color="#334155",
                    size=13
                )
            )
        ),

        legend=dict(
            font=dict(
                color="#334155",
                size=12
            )
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_color="#0F172A"
        )
    )

    st.plotly_chart(fig5, use_container_width=True)

# TAB 4 - ASK YOUR DATA
with tab4:
    st.subheader("Ask Your Data")

    if st.button(" Generate Business Insights", type="primary"):
        with st.spinner("Analysing your data..."):
            insight = ask_ai(
                "Give me the top 3 business insights with specific numbers and what the business should investigate.",
                analytics
            )
        st.success("Insights Generated")
        st.markdown(insight)

        st.divider()

    question = st.text_input(
        "Your question",
        placeholder="e.g. Why did sales decline in January 2024?",
        label_visibility="collapsed"
    )

    if st.button("Ask", type="secondary") and question:
        with st.spinner("Thinking..."):
            answer = ask_ai(question, analytics)

        st.markdown(
            f"""
            <div class="ai-answer">
                <div class="ai-answer-title">Answer</div>
                <div class="ai-answer-text">{answer}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        """
        <div class="questions-title">
            Try these questions
        </div>
        """,
        unsafe_allow_html=True
    )

    sample_questions = [
        "Which category generated the most revenue?",
        "Which region has the lowest profit margin?",
        "What anomalies were detected and what do they suggest?",
        "Which customer segment should we focus on?",
        "What should the business investigate urgently?"
    ]

    for i, q in enumerate(sample_questions):
        if st.button(q, key=f"sample_question_{i}"):
            with st.spinner("Thinking..."):
                answer = ask_ai(q, analytics)

            st.markdown(
                f"""
                <div class="ai-answer">
                    <div class="ai-answer-title">Answer</div>
                    <div class="ai-answer-text">{answer}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
