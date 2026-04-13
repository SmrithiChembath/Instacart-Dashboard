"""
Instacart Market Basket Analysis — Streamlit Dashboard
Real data: 75K users · 1.2M orders · 12.3M order-product rows
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Instacart Market Basket Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="metric-container"] {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)

# ── DB connection ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("instacart.db", check_same_thread=False)

conn = get_conn()

@st.cache_data(ttl=3600, show_spinner=False)
def query(sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)

# ── Sidebar ────────────────────────────────────────────────────────────────────
# st.sidebar.image("https://www.creativeboom.com/inspiration/wolff-olins-creates-new-identity-system-for-instacart-in-partnership-with-instacart-creative-studio/", width=180)
st.sidebar.title("Filters")

departments_df = query("SELECT department_id, department FROM departments ORDER BY department")
dept_options   = departments_df["department"].tolist()
selected_depts = st.sidebar.multiselect("Department", dept_options, default=dept_options[:5])

if not selected_depts:
    st.warning("Please select at least one department from the sidebar.")
    st.stop()

dept_ids = departments_df[departments_df["department"].isin(selected_depts)]["department_id"].tolist()
dept_placeholders = ",".join(["?" for _ in dept_ids])

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset Stats**")
st.sidebar.markdown("- 75,000 users sampled\n- 1.24M orders\n- 12.3M order-product rows\n- 49,688 products\n- 134 aisles · 21 departments")
st.sidebar.markdown("*Source: [Instacart Kaggle](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset)*")

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("🛒 Instacart Market Basket Analysis")
st.caption("Real grocery ordering data · SQLite + Streamlit + Plotly · 12.3M order-product rows")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 1. KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
kpi_sql = f"""
SELECT
    COUNT(DISTINCT o.order_id)                              AS total_orders,
    COUNT(DISTINCT o.user_id)                               AS unique_users,
    COUNT(op.rowid)                                         AS total_items,
    ROUND(COUNT(op.rowid) * 1.0 / COUNT(DISTINCT o.order_id), 1) AS avg_items_per_order,
    ROUND(AVG(CASE WHEN op.reordered = 1 THEN 100.0 ELSE 0 END), 1) AS reorder_rate_pct
FROM orders o
JOIN order_products op ON o.order_id = op.order_id
JOIN products p        ON op.product_id = p.product_id
WHERE p.department_id IN ({dept_placeholders})
"""
kpi = query(kpi_sql, tuple(dept_ids)).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🛒 Orders",         f"{int(kpi['total_orders']):,}")
c2.metric("👤 Users",          f"{int(kpi['unique_users']):,}")
c3.metric("📦 Items Ordered",  f"{int(kpi['total_items']):,}")
c4.metric("📊 Avg Items/Order",f"{kpi['avg_items_per_order']}")
c5.metric("🔁 Reorder Rate",   f"{kpi['reorder_rate_pct']}%")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 2. ORDERING PATTERNS — Hour of day & Day of week
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("⏰ When Do People Shop?")

col1, col2 = st.columns(2)

with col1:
    hour_sql = f"""
    SELECT o.order_hour_of_day AS hour,
           COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN order_products op ON o.order_id = op.order_id
    JOIN products p        ON op.product_id = p.product_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY o.order_hour_of_day
    ORDER BY o.order_hour_of_day
    """
    hour_df = query(hour_sql, tuple(dept_ids))
    hour_df["hour_label"] = hour_df["hour"].apply(lambda h: f"{h:02d}:00")

    fig_hour = px.bar(
        hour_df, x="hour_label", y="orders",
        color="orders", color_continuous_scale="Blues",
        labels={"hour_label": "Hour of Day", "orders": "Number of Orders"},
        title="Orders by Hour of Day"
    )
    fig_hour.update_layout(
        coloraxis_showscale=False, height=360,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=-45)
    )
    st.plotly_chart(fig_hour, use_container_width=True)

with col2:
    dow_sql = f"""
    SELECT o.order_dow AS dow,
           COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN order_products op ON o.order_id = op.order_id
    JOIN products p        ON op.product_id = p.product_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY o.order_dow
    ORDER BY o.order_dow
    """
    dow_df = query(dow_sql, tuple(dept_ids))
    day_names = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
                 4: "Thursday", 5: "Friday", 6: "Saturday"}
    dow_df["day"] = dow_df["dow"].map(day_names)

    fig_dow = px.bar(
        dow_df, x="day", y="orders",
        color="orders", color_continuous_scale="Greens",
        labels={"day": "Day of Week", "orders": "Number of Orders"},
        title="Orders by Day of Week",
        category_orders={"day": list(day_names.values())}
    )
    fig_dow.update_layout(
        coloraxis_showscale=False, height=360,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_dow, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. TOP PRODUCTS & REORDER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏆 Top 20 Most Ordered Products")
    top_prod_sql = f"""
    SELECT p.product_name,
           COUNT(op.rowid)                                          AS times_ordered,
           ROUND(AVG(op.reordered) * 100, 1)                       AS reorder_pct,
           d.department
    FROM order_products op
    JOIN products p    ON op.product_id = p.product_id
    JOIN departments d ON p.department_id = d.department_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY p.product_id
    ORDER BY times_ordered DESC
    LIMIT 20
    """
    top_prod = query(top_prod_sql, tuple(dept_ids))

    fig_top = px.bar(
        top_prod, x="times_ordered", y="product_name",
        orientation="h", color="reorder_pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        labels={"times_ordered": "Times Ordered", "product_name": "",
                "reorder_pct": "Reorder %"},
        title="Color = Reorder Rate (%)"
    )
    fig_top.update_layout(
        height=520, yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col4:
    st.subheader("🔁 Top 20 Most Reordered Products")
    reorder_sql = f"""
    SELECT p.product_name,
           COUNT(op.rowid)                        AS times_ordered,
           SUM(op.reordered)                       AS times_reordered,
           ROUND(AVG(op.reordered) * 100, 1)       AS reorder_pct
    FROM order_products op
    JOIN products p ON op.product_id = p.product_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY p.product_id
    HAVING times_ordered >= 100
    ORDER BY reorder_pct DESC
    LIMIT 20
    """
    reorder_df = query(reorder_sql, tuple(dept_ids))

    fig_reorder = px.bar(
        reorder_df, x="reorder_pct", y="product_name",
        orientation="h", color="times_ordered",
        color_continuous_scale="Purples",
        labels={"reorder_pct": "Reorder Rate (%)", "product_name": "",
                "times_ordered": "Total Orders"},
        title="Color = Total Order Volume"
    )
    fig_reorder.update_layout(
        height=520, yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_reorder, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 4. DEPARTMENT & AISLE BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
col5, col6 = st.columns(2)

with col5:
    st.subheader("🏪 Orders by Department")
    dept_sql = f"""
    SELECT d.department,
           COUNT(op.rowid)                           AS items_ordered,
           ROUND(AVG(op.reordered) * 100, 1)         AS reorder_pct
    FROM order_products op
    JOIN products p    ON op.product_id = p.product_id
    JOIN departments d ON p.department_id = d.department_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY d.department_id
    ORDER BY items_ordered DESC
    """
    dept_vol = query(dept_sql, tuple(dept_ids))

    fig_dept = px.pie(
        dept_vol, names="department", values="items_ordered",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_dept.update_traces(textposition="inside", textinfo="percent+label")
    fig_dept.update_layout(
        height=420, paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True, legend=dict(orientation="v", x=1.0)
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with col6:
    st.subheader("🥦 Top 15 Aisles by Order Volume")
    aisle_sql = f"""
    SELECT a.aisle,
           d.department,
           COUNT(op.rowid)                       AS items_ordered,
           ROUND(AVG(op.reordered) * 100, 1)     AS reorder_pct
    FROM order_products op
    JOIN products p    ON op.product_id = p.product_id
    JOIN aisles a      ON p.aisle_id = a.aisle_id
    JOIN departments d ON p.department_id = d.department_id
    WHERE p.department_id IN ({dept_placeholders})
    GROUP BY a.aisle_id
    ORDER BY items_ordered DESC
    LIMIT 15
    """
    aisle_df = query(aisle_sql, tuple(dept_ids))

    fig_aisle = px.bar(
        aisle_df, x="items_ordered", y="aisle",
        orientation="h", color="department",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"items_ordered": "Items Ordered", "aisle": ""}
    )
    fig_aisle.update_layout(
        height=420, yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_aisle, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 5. USER BEHAVIOUR — Order frequency & basket size
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("👤 User Behaviour Analysis")

col7, col8 = st.columns(2)

with col7:
    st.markdown("**Days Between Orders Distribution**")
    days_sql = """
    SELECT days_since_prior_order AS days,
           COUNT(*) AS orders
    FROM orders
    WHERE days_since_prior_order IS NOT NULL
      AND days_since_prior_order != ''
    GROUP BY days_since_prior_order
    ORDER BY CAST(days_since_prior_order AS REAL)
    """
    days_df = query(days_sql)
    days_df["days"] = pd.to_numeric(days_df["days"], errors="coerce")
    days_df = days_df.dropna()

    fig_days = px.bar(
        days_df, x="days", y="orders",
        color="orders", color_continuous_scale="Oranges",
        labels={"days": "Days Since Prior Order", "orders": "Number of Orders"}
    )
    fig_days.update_layout(
        coloraxis_showscale=False, height=340,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_days, use_container_width=True)

with col8:
    st.markdown("**Order Count Distribution per User**")
    user_orders_sql = """
    SELECT order_count,
           COUNT(*) AS num_users
    FROM (
        SELECT user_id, MAX(order_number) AS order_count
        FROM orders
        GROUP BY user_id
    )
    WHERE order_count <= 50
    GROUP BY order_count
    ORDER BY order_count
    """
    user_orders_df = query(user_orders_sql)

    fig_user = px.bar(
        user_orders_df, x="order_count", y="num_users",
        color="num_users", color_continuous_scale="Teal",
        labels={"order_count": "Number of Orders per User", "num_users": "Number of Users"}
    )
    fig_user.update_layout(
        coloraxis_showscale=False, height=340,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_user, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 6. CART POSITION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🛒 Cart Position Analysis")
st.caption("Which position in the cart do people add items? First-added items are likely essentials.")

cart_sql = f"""
SELECT op.add_to_cart_order AS cart_position,
       COUNT(op.rowid) AS items,
       ROUND(AVG(op.reordered) * 100, 1) AS reorder_pct
FROM order_products op
JOIN products p ON op.product_id = p.product_id
WHERE p.department_id IN ({dept_placeholders})
  AND op.add_to_cart_order <= 20
GROUP BY op.add_to_cart_order
ORDER BY op.add_to_cart_order
"""
cart_df = query(cart_sql, tuple(dept_ids))

fig_cart = make_subplots(specs=[[{"secondary_y": True}]])
fig_cart.add_trace(
    go.Bar(x=cart_df["cart_position"], y=cart_df["items"],
           name="Items Added", marker_color="#4F8EF7"),
    secondary_y=False
)
fig_cart.add_trace(
    go.Scatter(x=cart_df["cart_position"], y=cart_df["reorder_pct"],
               name="Reorder Rate (%)", mode="lines+markers",
               line=dict(color="#FF6B6B", width=2), marker=dict(size=6)),
    secondary_y=True
)
fig_cart.update_xaxes(title_text="Position Added to Cart")
fig_cart.update_yaxes(title_text="Number of Items", secondary_y=False)
fig_cart.update_yaxes(title_text="Reorder Rate (%)", secondary_y=True)
fig_cart.update_layout(
    height=380, paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)", legend=dict(x=0.7, y=1.1)
)
st.plotly_chart(fig_cart, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 7. LIVE SQL EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🔎 Live SQL Explorer")
st.caption("Tables: `orders`, `order_products`, `products`, `aisles`, `departments`")

example_queries = {
    "Department reorder rates": """SELECT d.department,
       COUNT(op.rowid)                         AS total_items,
       SUM(op.reordered)                        AS reordered_items,
       ROUND(AVG(op.reordered) * 100, 2)        AS reorder_rate_pct
FROM order_products op
JOIN products p    ON op.product_id = p.product_id
JOIN departments d ON p.department_id = d.department_id
GROUP BY d.department
ORDER BY reorder_rate_pct DESC;""",

    "Top 10 products in produce": """SELECT p.product_name,
       COUNT(op.rowid)  AS times_ordered
FROM order_products op
JOIN products p    ON op.product_id = p.product_id
JOIN departments d ON p.department_id = d.department_id
WHERE d.department = 'produce'
GROUP BY p.product_id
ORDER BY times_ordered DESC
LIMIT 10;""",

    "Avg basket size by day of week": """SELECT
    CASE order_dow
        WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day,
    ROUND(COUNT(op.rowid) * 1.0 / COUNT(DISTINCT o.order_id), 2) AS avg_basket_size
FROM orders o
JOIN order_products op ON o.order_id = op.order_id
GROUP BY o.order_dow
ORDER BY o.order_dow;"""
}

selected_example = st.selectbox("Load an example query:", ["(write your own)"] + list(example_queries.keys()))
default_sql = example_queries.get(selected_example, list(example_queries.values())[0])

user_sql = st.text_area("SQL", value=default_sql, height=160)

if st.button("▶  Run Query", type="primary"):
    try:
        result = query(user_sql)
        st.dataframe(result, use_container_width=True)
        st.caption(f"✅ {len(result):,} rows returned")
        if len(result.columns) == 2:
            fig_auto = px.bar(result, x=result.columns[0], y=result.columns[1])
            fig_auto.update_layout(height=320, plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_auto, use_container_width=True)
    except Exception as e:
        st.error(f"Query error: {e}")
