import json
import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

import database


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# PREMIUM DASHBOARD STYLING
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080d1b;
    --panel: #111a2e;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
    --pink: #f472b6;
    --muted: #a5b4fc;
}

.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, #201442 0%, transparent 38%),
        radial-gradient(ellipse at 100% 10%, #0b2940 0%, transparent 35%),
        var(--bg);
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #10152b, #0b1221);
    border-right: 1px solid rgba(139, 92, 246, .25);
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

h1, h2, h3 {
    color: #f5f3ff !important;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #c4b5fd, #67e8f9, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #151f35, #10172a);
    border: 1px solid rgba(139, 92, 246, .3);
    border-radius: 16px;
    padding: 18px;
    animation: fadeUp .45s ease both;
    transition: transform .2s ease, border-color .2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: #22d3ee;
}

[data-testid="stMetricLabel"] {
    color: #a5b4fc !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 800;
}

div[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: rgba(139, 92, 246, .28);
    border-radius: 16px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(100deg, #9333ea, #6366f1, #0891b2);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    transition: transform .2s ease, box-shadow .2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 18px rgba(139, 92, 246, .35);
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(139, 92, 246, .25);
    border-radius: 12px;
}

[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #8b5cf6, #22d3ee);
}

hr {
    border-color: rgba(139, 92, 246, .2);
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)



# ==================================================
# PERSONALIZED WELCOME PAGE
# ==================================================

PROFILE_FILE = Path(__file__).resolve().parent / "profile.json"


def load_profile():
    """Load the saved user profile, if one exists."""
    if not PROFILE_FILE.exists():
        return {}

    try:
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_profile(name=None, theme=None):
    """Update profile fields while preserving existing preferences."""
    current = load_profile()
    if name is not None:
        current["name"] = name
    if theme is not None:
        current["theme"] = theme
    PROFILE_FILE.write_text(
        json.dumps(current, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


profile = load_profile()
user_name = str(profile.get("name", "")).strip()
current_theme = profile.get("theme", "Dark")
if current_theme not in ("Dark", "Light"):
    current_theme = "Dark"

if current_theme == "Light":
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at 0% 0%, #ede9fe 0%, transparent 38%),
                    radial-gradient(ellipse at 100% 10%, #cffafe 0%, transparent 35%),
                    #f8fafc !important;
        color: #172033 !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff, #eef2ff) !important;
        border-right: 1px solid #d8dcef !important;
    }
    h1, h2, h3, p, label, [data-testid="stMarkdownContainer"] {
        color: #172033;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff, #f1f5f9) !important;
        border: 1px solid #d8dcef !important;
    }
    [data-testid="stMetricLabel"] { color: #475569 !important; }
    [data-testid="stMetricValue"] { color: #0f172a !important; }
    [data-testid="stDataFrame"] { border: 1px solid #d8dcef !important; }
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #d8dcef !important;
    }
    </style>
    """, unsafe_allow_html=True)

if not user_name:
    st.markdown(
        """
        <div style="text-align:center; padding:55px 10px 25px;">
            <div style="font-size:64px;">💰</div>
            <h1>Smart Expense Tracker</h1>
            <p style="color:#A5B4FC; font-size:17px;">
                Your money. Your goals. Your control.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, welcome_col, _ = st.columns([1, 1.4, 1])

    with welcome_col:
        with st.form("welcome_form"):
            name_input = st.text_input(
                "What should we call you?",
                placeholder="Enter your name...",
                max_chars=50,
            )

            start = st.form_submit_button(
                "✨ Let's Get Started",
                use_container_width=True,
            )

            if start:
                clean_name = " ".join(name_input.split())

                if not clean_name:
                    st.error("Please enter your name.")
                elif any(ord(char) < 32 for char in clean_name):
                    st.error("Please enter a valid name.")
                else:
                    try:
                        save_profile(clean_name)
                        st.rerun()
                    except OSError:
                        st.error(
                            "Could not save your name. "
                            "Check that the project folder is writable."
                        )

    st.stop()


# ==================================================
# INITIALIZE DATA
# ==================================================

database.initialize_database()

transactions = database.get_transactions()
summary = database.get_summary()
budgets = database.get_category_budgets()

today = date.today()

budget_categories = [
    "Food", "Travel", "Education", "Shopping",
    "Bills", "Health", "Entertainment", "Other"
]

income_categories = [
    "Salary", "Freelance", "Pocket Money",
    "Investment", "Other"
]

df = pd.DataFrame(transactions)

if not df.empty:
    df["expense_date"] = pd.to_datetime(
        df["expense_date"], errors="coerce"
    )


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:
    st.markdown(
        "<h2 style='font-size:23px;'>💰 Smart <span "
        "style='color:#22d3ee;'>Expense</span></h2>",
        unsafe_allow_html=True,
    )

    st.caption("PERSONAL FINANCE DASHBOARD")
    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "📋 Transactions",
            "📊 Analytics",
            "🤖 AI Insights",
            "🎯 Budgets",
            "⚙️ Settings",
        ],
        label_visibility="visible",
    )

    st.divider()
    st.markdown("### 🎨 Appearance")
    selected_theme = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if current_theme == "Dark" else 1,
        key="sidebar_theme_selector",
    )
    if selected_theme != current_theme:
        try:
            save_profile(theme=selected_theme)
            st.rerun()
        except OSError:
            st.error("Could not save the theme preference.")

    st.divider()

    st.markdown("### ✨ Your money, organized")
    st.caption("Track smarter. Spend wisely.")
    st.caption("Built with Python + Streamlit")


# ==================================================
# REUSABLE CHART STYLE
# ==================================================

def style_chart(fig, height=350):
    chart_template = "plotly_white" if current_theme == "Light" else "plotly_dark"
    chart_font_color = "#334155" if current_theme == "Light" else "#dbeafe"
    fig.update_layout(
        template=chart_template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color=chart_font_color,
        ),
        margin=dict(l=15, r=15, t=55, b=15),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ==================================================
# HEADER
# ==================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title(f"Hello, {user_name}! 👋")
    st.caption(
        "Track your income, expenses and monthly budget."
    )

with header_right:
    st.markdown(
        f"<div style='text-align:right;padding-top:15px;"
        f"color:#a5b4fc;font-weight:600;'>"
        f"📅 {today.strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True,
    )


def render_budget_alert(category, spent, limit):
    """Show clear alerts at 80% and 100% of a category's monthly budget."""
    if limit <= 0:
        return

    usage = spent / limit
    if usage >= 1:
        over_by = spent - limit
        st.error(
            f"🚨 **{category}: budget exceeded!** "
            f"Spent ₹{spent:,.2f} of ₹{limit:,.2f} "
            f"({usage:.0%}). Over budget by ₹{over_by:,.2f}."
        )
    elif usage >= 0.8:
        st.warning(
            f"⚠️ **{category}: budget almost used!** "
            f"Spent ₹{spent:,.2f} of ₹{limit:,.2f} "
            f"({usage:.0%}). Only ₹{limit - spent:,.2f} remaining."
        )
    else:
        st.caption(f"✅ {category}: {usage:.0%} of monthly budget used.")


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    # Four overview cards
    active_budgets = len(budgets)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💚 Total Income",
        f"₹{summary['total_income']:,.2f}",
    )

    c2.metric(
        "💸 Total Expenses",
        f"₹{summary['total_expenses']:,.2f}",
    )

    c3.metric(
        "💎 Current Balance",
        f"₹{summary['balance']:,.2f}",
    )

    c4.metric(
        "🎯 Active Budgets",
        str(active_budgets),
        help="Number of categories with saved budgets.",
    )

    st.divider()

    # Main dashboard columns
    left, right = st.columns([1, 1.65], gap="large")

    # Add transaction form
    with left:
        st.subheader("➕ Add a Transaction")

        with st.form("dashboard_transaction_form",
                     clear_on_submit=True):

            entry_type = st.selectbox(
                "Transaction Type",
                ["Expense", "Income"],
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=100.0,
                step=50.0,
            )

            categories = (
                budget_categories
                if entry_type == "Expense"
                else income_categories
            )

            category = st.selectbox(
                "Category", categories
            )

            description = st.text_input(
                "Description (optional)"
            )

            transaction_date = st.date_input(
                "Date", value=today
            )

            submitted = st.form_submit_button(
                "💾 Save Transaction",
                use_container_width=True,
            )

            if submitted:
                try:
                    database.add_transaction(
                        entry_type,
                        amount,
                        category,
                        description,
                        transaction_date.isoformat(),
                    )

                    st.success("Transaction saved!")
                    st.rerun()

                except (ValueError, Exception) as error:
                    st.error(f"Could not save: {error}")

    # Recent transactions
    with right:
        st.subheader("📋 Recent Transactions")

        if not df.empty:
            recent = df.head(5).copy()

            recent = recent.rename(
                columns={
                    "id": "ID",
                    "entry_type": "Type",
                    "amount": "Amount (₹)",
                    "category": "Category",
                    "description": "Description",
                    "expense_date": "Date",
                }
            )

            recent["Date"] = recent["Date"].dt.strftime(
                "%d %b %Y"
            )

            st.dataframe(
                recent[
                    [
                        "ID", "Type", "Amount (₹)",
                        "Category", "Description", "Date"
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            if st.button("View All Transactions →"):
                st.session_state["requested_page"] = (
                    "📋 Transactions"
                )
                st.rerun()

        else:
            st.info("Add your first transaction to get started.")

    st.divider()

    # Charts
    chart_left, chart_right = st.columns(
        [1.2, 1], gap="large"
    )

    with chart_left:
        st.subheader("📊 Spending by Category")

        if not df.empty:
            expenses = df[
                df["entry_type"] == "Expense"
            ]

            if not expenses.empty:
                category_totals = (
                    expenses.groupby("category")["amount"]
                    .sum()
                    .reset_index()
                )

                fig = px.pie(
                    category_totals,
                    names="category",
                    values="amount",
                    hole=0.58,
                    color_discrete_sequence=[
                        "#8b5cf6", "#22d3ee", "#f472b6",
                        "#34d399", "#fbbf24", "#60a5fa",
                        "#fb7185", "#a3e635",
                    ],
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    marker=dict(
                        line=dict(
                            color="#080d1b",
                            width=3,
                        )
                    ),
                )

                style_chart(fig)
                st.plotly_chart(
                    fig, use_container_width=True
                )
            else:
                st.info("Your expense chart will appear here.")
        else:
            st.info("Add transactions to see spending analytics.")

    with chart_right:
        st.subheader("📈 Monthly Trend")

        if not df.empty:
            monthly = df.copy()

            monthly["Month"] = (
                monthly["expense_date"].dt.to_period("M")
            )

            monthly = (
                monthly.groupby(["Month", "entry_type"])["amount"]
                .sum()
                .reset_index()
            )

            monthly["Month"] = (
                monthly["Month"].astype(str)
            )

            fig = px.bar(
                monthly,
                x="Month",
                y="amount",
                color="entry_type",
                barmode="group",
                color_discrete_map={
                    "Income": "#34d399",
                    "Expense": "#f472b6",
                },
                labels={
                    "amount": "Amount (₹)",
                    "entry_type": "Type",
                },
            )

            style_chart(fig)
            st.plotly_chart(
                fig, use_container_width=True
            )
        else:
            st.info("Monthly trends will appear here.")

    st.divider()

    # Budget overview
    st.subheader("🎯 Category-wise Monthly Budgets")

    month_spending = (
        database.get_monthly_category_spending(
            today.year, today.month
        )
    )

    if not budgets:
        st.info("No budgets set yet. Open Budgets to add one.")
    else:
        for budget in budgets:
            category = budget["category"]
            limit = budget["monthly_limit"]
            spent = month_spending.get(category, 0.0)
            remaining = limit - spent

            with st.container(border=True):
                b1, b2, b3 = st.columns([2, 1, 1])

                b1.markdown(f"**🎯 {category}**")
                b1.caption(
                    f"₹{spent:,.2f} spent of ₹{limit:,.2f}"
                )

                b2.metric(
                    "Spent",
                    f"₹{spent:,.2f}",
                )

                b3.metric(
                    "Remaining" if remaining >= 0 else "Over budget",
                    f"₹{abs(remaining):,.2f}",
                )

                usage = spent / limit if limit > 0 else 0
                st.progress(min(usage, 1.0))
                render_budget_alert(category, spent, limit)


# ==================================================
# TRANSACTIONS PAGE
# ==================================================

elif page == "📋 Transactions":

    st.header("📋 All Transactions")
    st.caption("Review and delete saved records.")

    if df.empty:
        st.info("No transactions available.")
    else:
        search = st.text_input(
            "🔎 Search category or description"
        )

        filtered = df.copy()

        if search.strip():
            mask = (
                filtered["category"].str.contains(
                    search, case=False, na=False
                )
                | filtered["description"].str.contains(
                    search, case=False, na=False
                )
            )
            filtered = filtered[mask]

        st.dataframe(
            filtered.rename(
                columns={
                    "id": "ID",
                    "entry_type": "Type",
                    "amount": "Amount (₹)",
                    "category": "Category",
                    "description": "Description",
                    "expense_date": "Date",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("🗑️ Delete Transaction")

        selected_id = st.selectbox(
            "Select transaction ID",
            [item["id"] for item in transactions],
        )

        if st.button("Delete Selected Transaction"):
            if database.delete_transaction(selected_id):
                st.success("Transaction deleted.")
                st.rerun()
            else:
                st.error("Transaction not found.")


# ==================================================
# ANALYTICS PAGE
# ==================================================

elif page == "📊 Analytics":

    st.header("📊 Financial Analytics")
    st.caption("Understand your spending patterns.")

    if df.empty:
        st.info("Add transactions to unlock analytics.")
    else:
        expenses = df[
            df["entry_type"] == "Expense"
        ]

        income = df[
            df["entry_type"] == "Income"
        ]

        a1, a2, a3 = st.columns(3)

        a1.metric(
            "Transactions",
            len(df),
        )

        a2.metric(
            "Average Expense",
            f"₹{expenses['amount'].mean():,.2f}"
            if not expenses.empty else "₹0.00",
        )

        a3.metric(
            "Income Records",
            len(income),
        )

        if not expenses.empty:
            st.subheader("Category Comparison")

            cat_df = (
                expenses.groupby("category")["amount"]
                .sum()
                .reset_index()
                .sort_values("amount", ascending=True)
            )

            fig = px.bar(
                cat_df,
                x="amount",
                y="category",
                orientation="h",
                color="amount",
                color_continuous_scale=[
                    "#312e81", "#8b5cf6", "#22d3ee"
                ],
                labels={
                    "amount": "Total Spending (₹)",
                    "category": "Category",
                },
            )

            style_chart(fig, height=420)
            st.plotly_chart(
                fig, use_container_width=True
            )

        st.subheader("Transaction Timeline")

        timeline = df.copy()
        timeline["Day"] = (
            timeline["expense_date"].dt.date
        )

        timeline = (
            timeline.groupby(["Day", "entry_type"])["amount"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            timeline,
            x="Day",
            y="amount",
            color="entry_type",
            markers=True,
            color_discrete_map={
                "Income": "#34d399",
                "Expense": "#f472b6",
            },
        )

        style_chart(fig)
        st.plotly_chart(
            fig, use_container_width=True
        )


# ==================================================
# FREE PYTHON-BASED AI EXPENSE INSIGHTS
# ==================================================

elif page == "🤖 AI Insights":

    st.header("🤖 Smart Expense Insights")
    st.caption(
        "Personalized, rule-based financial insights generated locally from your saved transactions — no paid API or API key required."
    )

    if df.empty:
        st.info("Add a few income or expense transactions first. Your insights will appear here automatically.")
    else:
        insight_df = df.copy()
        insight_df["expense_date"] = pd.to_datetime(
            insight_df["expense_date"], errors="coerce"
        )
        insight_df["amount"] = pd.to_numeric(
            insight_df["amount"], errors="coerce"
        ).fillna(0)
        insight_df = insight_df.dropna(subset=["expense_date"])
        current_month = insight_df[
            (insight_df["expense_date"].dt.year == today.year)
            & (insight_df["expense_date"].dt.month == today.month)
        ]
        month_expenses = current_month[
            current_month["entry_type"].astype(str).str.lower() == "expense"
        ]
        month_income = current_month[
            current_month["entry_type"].astype(str).str.lower() == "income"
        ]
        total_month_spend = float(month_expenses["amount"].sum())
        total_month_income = float(month_income["amount"].sum())
        days_elapsed = max(today.day, 1)
        days_in_month = pd.Timestamp(today.year, today.month, 1).days_in_month
        daily_average = total_month_spend / days_elapsed
        projected_spend = daily_average * days_in_month
        net_cashflow = total_month_income - total_month_spend

        st.subheader(f"📅 Snapshot — {today.strftime('%B %Y')}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Month's Expenses", f"₹{total_month_spend:,.2f}")
        m2.metric("Month's Income", f"₹{total_month_income:,.2f}")
        m3.metric("Net Cash Flow", f"₹{net_cashflow:,.2f}")
        m4.metric("Estimated Month-End Spend", f"₹{projected_spend:,.2f}")
        st.caption(
            f"Projection uses this month's average spend so far (₹{daily_average:,.2f}/day) and assumes the pace stays similar. It is an estimate, not a guarantee."
        )

        st.divider()
        st.subheader("🧠 Your Smart Recommendations")
        insights_count = 0

        if total_month_spend == 0:
            st.success("No expenses recorded for this month yet. Add transactions as you go to build a useful spending picture.")
            insights_count += 1
        else:
            if total_month_income > 0:
                spend_ratio = total_month_spend / total_month_income
                if spend_ratio >= 1:
                    st.warning(f"Your recorded expenses are {spend_ratio * 100:.0f}% of recorded income this month. Review non-essential spending if you can.")
                elif spend_ratio >= 0.8:
                    st.warning(f"You've used {spend_ratio * 100:.0f}% of your recorded monthly income. Keep an eye on upcoming expenses.")
                else:
                    st.success(f"Recorded expenses are {spend_ratio * 100:.0f}% of recorded income this month. Keep tracking to maintain a clear picture.")
                insights_count += 1

            if not month_expenses.empty:
                category_spend = (
                    month_expenses.groupby("category")["amount"]
                    .sum().sort_values(ascending=False)
                )
                top_category = str(category_spend.index[0])
                top_amount = float(category_spend.iloc[0])
                top_share = top_amount / total_month_spend * 100 if total_month_spend else 0
                st.info(f"Your highest-spending category this month is **{top_category}** at **₹{top_amount:,.2f}** ({top_share:.0f}% of recorded expenses). If you want to cut spending, start by reviewing this category.")
                insights_count += 1

                if budgets:
                    budget_map = {str(item.get("category")): float(item.get("monthly_limit", 0) or 0) for item in budgets}
                    for category, amount in category_spend.items():
                        limit = budget_map.get(str(category), 0)
                        if limit > 0 and float(amount) >= limit * 0.8:
                            if float(amount) >= limit:
                                st.error(f"Budget alert — **{category}** is at/over its monthly limit: ₹{float(amount):,.2f} spent against ₹{limit:,.2f}.")
                            else:
                                st.warning(f"Budget heads-up — **{category}** has used {float(amount) / limit * 100:.0f}% of its ₹{limit:,.2f} limit; ₹{limit - float(amount):,.2f} remains.")
                            insights_count += 1

                if projected_spend > total_month_spend and days_elapsed < days_in_month:
                    st.caption(f"At the current pace, spending could reach about ₹{projected_spend:,.2f} by month-end — roughly ₹{projected_spend - total_month_spend:,.2f} more than recorded so far.")
                    insights_count += 1

        st.divider()
        st.subheader("📊 Monthly Category Breakdown")
        if month_expenses.empty:
            st.info("No expense entries found for the current month.")
        else:
            category_df = (
                month_expenses.groupby("category", as_index=False)["amount"]
                .sum().sort_values("amount", ascending=False)
            )
            category_df["Share of Expenses"] = (
                category_df["amount"] / total_month_spend * 100
            ).round(1)
            category_df = category_df.rename(columns={
                "category": "Category", "amount": "Spent (₹)"
            })
            st.dataframe(category_df, use_container_width=True, hide_index=True)
            fig = px.pie(
                category_df, names="Category", values="Spent (₹)",
                hole=0.55, title="Where this month's money went"
            )
            style_chart(fig, height=380)
            st.plotly_chart(fig, use_container_width=True)

        # ==================================================
        # ADVANCED FINANCIAL INTELLIGENCE (OPTION 4)
        # Read-only analysis: does not alter the SQLite database.
        # ==================================================
        st.divider()
        st.header("🧠 Advanced Financial Intelligence")
        st.caption("Historical comparison, unusual-spend flags, and a savings-goal planner. These are rule-based estimates, not financial advice.")

        # Normalize transaction data for safe analysis.
        history = insight_df.copy()
        history["entry_type_norm"] = history["entry_type"].astype(str).str.strip().str.lower()
        expense_history = history[history["entry_type_norm"] == "expense"].copy()
        expense_history = expense_history.dropna(subset=["expense_date"])
        expense_history["month"] = expense_history["expense_date"].dt.to_period("M")
        current_period = pd.Period(today, freq="M")
        previous_period = current_period - 1
        current_total = float(expense_history.loc[expense_history["month"] == current_period, "amount"].sum())
        previous_total = float(expense_history.loc[expense_history["month"] == previous_period, "amount"].sum())

        st.subheader("📆 Month-to-Month Spending")
        compare_left, compare_right = st.columns(2)
        compare_left.metric(f"{previous_period.strftime('%B %Y')} expenses", f"₹{previous_total:,.2f}")
        delta_value = current_total - previous_total
        if previous_total > 0:
            delta_pct = delta_value / previous_total * 100
            delta_label = f"{delta_pct:+.1f}% vs previous month"
        elif current_total > 0:
            delta_label = "No previous-month expenses to compare"
        else:
            delta_label = "No expenses recorded in either month"
        compare_right.metric(f"{current_period.strftime('%B %Y')} expenses", f"₹{current_total:,.2f}", delta=delta_label, delta_color="inverse" if previous_total > 0 else "off")
        if previous_total > 0:
            if current_total > previous_total:
                st.warning(f"Recorded spending is ₹{delta_value:,.2f} ({delta_value / previous_total * 100:.1f}%) higher than last month. This comparison uses recorded transactions only.")
            elif current_total < previous_total:
                st.success(f"Recorded spending is ₹{abs(delta_value):,.2f} ({abs(delta_value) / previous_total * 100:.1f}%) lower than last month.")
            else:
                st.info("Recorded spending is unchanged from last month.")
        else:
            st.info("A month-to-month percentage comparison becomes available once the previous month has recorded expenses.")

        # Always display the latest six calendar months, including months
        # with zero recorded expenses. Categorical month labels avoid time-axis formatting.
        display_periods = pd.period_range(
            start=current_period - 5,
            end=current_period,
            freq="M",
        )
        if not expense_history.empty:
            month_totals = expense_history.groupby("month")["amount"].sum()
        else:
            month_totals = pd.Series(dtype="float64")

        hist_df = pd.DataFrame({
            "Month": [period.strftime("%b %Y") for period in display_periods],
            "Month key": [str(period) for period in display_periods],
            "Expenses (₹)": [
                float(month_totals.get(period, 0.0))
                for period in display_periods
            ],
        })
        hist_fig = px.bar(
            hist_df,
            x="Month",
            y="Expenses (₹)",
            title="Recorded expenses — last 6 months",
            custom_data=["Month key"],
            text="Expenses (₹)",
        )
        hist_fig.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=hist_df["Month"].tolist(),
            tickmode="array",
            tickvals=hist_df["Month"].tolist(),
            ticktext=hist_df["Month"].tolist(),
            tickangle=0,
        )
        hist_fig.update_traces(
            texttemplate="₹%{y:,.0f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Expenses: ₹%{y:,.2f}<extra></extra>",
        )
        hist_fig.update_layout(
            yaxis=dict(rangemode="tozero"),
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )
        style_chart(hist_fig, height=360)
        st.plotly_chart(hist_fig, use_container_width=True)

        st.divider()
        st.subheader("🚨 Unusual Expense Detection")
        st.caption("Flags an expense only when it is at least ₹200 and more than twice the median transaction amount in that category. This is a simple screening rule, not proof that a transaction is wrong.")
        if expense_history.empty:
            st.info("Add expense transactions to detect unusual spending.")
        else:
            flagged = []
            for category, group in expense_history.groupby("category", dropna=False):
                amounts = pd.to_numeric(group["amount"], errors="coerce").dropna()
                if amounts.empty:
                    continue
                baseline = float(amounts.median())
                threshold = max(200.0, baseline * 2)
                candidates = group[pd.to_numeric(group["amount"], errors="coerce") >= threshold].copy()
                # Do not flag every transaction when a category only has a single record.
                if len(amounts) < 3:
                    continue
                for _, transaction in candidates.iterrows():
                    if float(transaction["amount"]) > baseline * 2:
                        flagged.append({"Date": transaction["expense_date"].strftime("%d %b %Y"), "Category": str(category), "Amount (₹)": float(transaction["amount"]), "Category median (₹)": baseline, "Rule": "Over 2× category median"})
            if flagged:
                flagged_df = pd.DataFrame(flagged).sort_values("Amount (₹)", ascending=False)
                st.warning(f"Found {len(flagged_df)} transaction(s) worth reviewing.")
                st.dataframe(flagged_df, use_container_width=True, hide_index=True)
            else:
                st.success("No transactions matched the unusual-spending rule. Categories need at least 3 recorded expenses before this check runs.")

        st.divider()
        st.subheader("🎯 Savings Goal Planner")
        st.caption("Your goal is saved per calendar month in SQLite and remains available after restarting the app.")

        saved_goal = database.get_savings_goal(today.year, today.month)
        default_baseline = (
            float(saved_goal["reference_spending"])
            if saved_goal else float(previous_total if previous_total > 0 else current_total)
        )
        default_reduction = (
            float(saved_goal["reduction_target"])
            if saved_goal else 500.0
        )

        with st.form("persistent_savings_goal_form"):
            goal_col1, goal_col2 = st.columns(2)
            savings_goal = goal_col1.number_input(
                "Monthly spending-reduction target (₹)",
                min_value=0.0, max_value=10000000.0,
                value=default_reduction, step=100.0,
                key=f"savings_reduction_{today.year}_{today.month}",
            )
            goal_baseline = goal_col2.number_input(
                "Reference monthly spending (₹)",
                min_value=0.0, max_value=10000000.0,
                value=default_baseline, step=100.0,
                key=f"savings_baseline_{today.year}_{today.month}",
            )
            save_goal_clicked = st.form_submit_button(
                "💾 Save Monthly Goal", use_container_width=True
            )

        if save_goal_clicked:
            try:
                database.set_savings_goal(
                    today.year, today.month, savings_goal, goal_baseline
                )
                st.success(
                    f"Savings goal saved for {today.strftime('%B %Y')}."
                )
                st.rerun()
            except (ValueError, sqlite3.Error) as error:
                st.error(f"Could not save savings goal: {error}")

        goal_target = max(float(goal_baseline) - float(savings_goal), 0.0)
        remaining_to_target = max(goal_target - current_total, 0.0)
        amount_over_target = max(current_total - goal_target, 0.0)
        progress = (
            min(current_total / goal_target, 1.0) if goal_target > 0
            else (1.0 if current_total == 0 else 0.0)
        )

        goal_metric_col1, goal_metric_col2, goal_metric_col3 = st.columns(3)
        goal_metric_col1.metric(
            "Target spending this month", f"₹{goal_target:,.2f}"
        )
        goal_metric_col2.metric(
            "Current recorded spending", f"₹{current_total:,.2f}"
        )
        goal_metric_col3.metric(
            "Room left before target", f"₹{remaining_to_target:,.2f}"
            if current_total <= goal_target else f"₹{amount_over_target:,.2f} over"
        )
        st.progress(progress, text=f"Target usage: {progress:.0%}")

        if current_total <= goal_target:
            st.success(
                f"You're within the target by ₹{remaining_to_target:,.2f} "
                "based on currently recorded expenses."
            )
        else:
            st.warning(
                f"Recorded spending is ₹{amount_over_target:,.2f} above "
                "this target. You can adjust the goal to fit your circumstances."
            )
        if saved_goal:
            st.caption(
                f"Saved for {today.strftime('%B %Y')} · Last updated: "
                f"{saved_goal.get('updated_at', 'date unavailable')}"
            )
        else:
            st.info("This month's goal has not been saved yet. Choose values and click Save Monthly Goal.")

        st.divider()
        st.subheader("💚 Financial Health Snapshot")
        health_a, health_b, health_c = st.columns(3)
        health_a.metric("Categories with budgets", str(len(budgets)))
        health_b.metric("Categories at 80%+ budget", str(sum(1 for item in budgets if float(item.get("monthly_limit", 0) or 0) > 0 and float(category_spend.get(str(item.get("category")), 0) if 'category_spend' in locals() else 0) / float(item.get("monthly_limit", 1)) >= 0.8)))
        health_c.metric("Recorded months", str(expense_history["month"].nunique() if not expense_history.empty else 0))
        st.caption("Health snapshot reports data coverage and budget pressure; it is not a credit score or a complete measure of financial health.")

        st.caption("Privacy note: this version uses your existing local app data and simple Python rules. It does not send transaction details to an external AI service.")


# ==================================================
# BUDGETS PAGE
# ==================================================

elif page == "🎯 Budgets":

    st.header("🎯 Budget Manager")
    st.caption(
        "Create and update monthly limits for expense categories."
    )

    with st.form("manage_budget_form"):

        budget_category = st.selectbox(
            "Category",
            budget_categories,
        )

        monthly_limit = st.number_input(
            "Monthly Limit (₹)",
            min_value=0.01,
            value=2000.0,
            step=100.0,
        )

        save_budget = st.form_submit_button(
            "💾 Save / Update Budget",
            use_container_width=True,
        )

        if save_budget:
            try:
                database.set_category_budget(
                    budget_category,
                    monthly_limit,
                )

                st.success(
                    f"{budget_category} budget saved."
                )
                st.rerun()

            except (ValueError, Exception) as error:
                st.error(f"Could not save budget: {error}")

    st.divider()
    st.subheader(
        f"📅 Budget Overview — {today.strftime('%B %Y')}"
    )

    month_spending = (
        database.get_monthly_category_spending(
            today.year, today.month
        )
    )

    budgets = database.get_category_budgets()

    if not budgets:
        st.info("Create your first budget above.")
    else:
        for budget in budgets:
            category = budget["category"]
            limit = budget["monthly_limit"]
            spent = month_spending.get(category, 0.0)
            remaining = limit - spent

            st.markdown(f"### {category}")

            c1, c2, c3 = st.columns(3)

            c1.metric("Monthly Budget", f"₹{limit:,.2f}")
            c2.metric("Spent", f"₹{spent:,.2f}")
            c3.metric(
                "Remaining" if remaining >= 0 else "Over Budget",
                f"₹{abs(remaining):,.2f}",
            )

            usage = spent / limit if limit > 0 else 0
            st.progress(min(usage, 1.0))
            render_budget_alert(category, spent, limit)

            st.divider()


# ==================================================
# SETTINGS PAGE
# ==================================================

elif page == "⚙️ Settings":

    st.header("⚙️ Profile & Settings")
    st.caption("Manage your display name and app appearance.")

    st.subheader("👤 Your Profile")
    with st.form("profile_settings_form"):
        updated_name = st.text_input(
            "Display name",
            value=user_name,
            max_chars=50,
            help="This name appears in your dashboard greeting.",
        )
        updated_theme = st.selectbox(
            "Appearance theme",
            ["Dark", "Light"],
            index=0 if current_theme == "Dark" else 1,
            help="Choose the look you prefer. Your choice is saved locally.",
        )
        save_settings = st.form_submit_button(
            "💾 Save Profile Settings",
            use_container_width=True,
        )
        if save_settings:
            clean_name = " ".join(updated_name.split())
            if not clean_name:
                st.error("Display name cannot be empty.")
            elif any(ord(char) < 32 for char in clean_name):
                st.error("Please enter a valid display name.")
            else:
                try:
                    save_profile(name=clean_name, theme=updated_theme)
                    st.success("Profile settings saved!")
                    st.rerun()
                except OSError:
                    st.error("Could not save settings. Check folder permissions.")

    st.caption("Your profile preferences are stored locally in `profile.json`.")
    st.divider()
    st.subheader("💻 Application Information")
    st.write("**Name:** Smart Expense Tracker")
    st.write("**Interface:** Streamlit")
    st.write("**Storage:** SQLite")
    st.write("**Charts:** Plotly")
    st.write("**Data processing:** Pandas")

    st.divider()
    st.subheader("📊 Your Data")
    s1, s2 = st.columns(2)
    s1.metric("Saved Transactions", len(transactions))
    s2.metric("Configured Budgets", len(budgets))
    st.info(
        "Your transactions and budgets remain in the local SQLite database. "
        "Changing profile settings does not delete or modify your expense records."
    )

    st.divider()
    st.subheader("↩️ Reset Welcome Profile")
    st.caption(
        "This removes the saved display name and theme preference only. "
        "It does not delete transactions or budgets."
    )
    confirm_reset = st.checkbox(
        "I understand this resets only my profile preferences.",
        key="confirm_profile_reset",
    )
    if st.button("Reset Profile", disabled=not confirm_reset):
        try:
            if PROFILE_FILE.exists():
                PROFILE_FILE.unlink()
            st.success("Profile preferences reset. The welcome page will appear next.")
            st.rerun()
        except OSError:
            st.error("Could not reset profile. Check folder permissions.")


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:14px;
        color:#94a3b8;
        font-size:13px;
    ">
        Built with 💜 Python, Streamlit, SQLite & Plotly
        <br>
        <span style="color:#22d3ee;">
            Smart Expense Tracker
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
