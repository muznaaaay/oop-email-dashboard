#!/usr/bin/env python3
"""Beehiiv Email Dashboard — Streamlit App."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from auth import check_password
import data

st.set_page_config(
    page_title="OOP Email Dashboard",
    page_icon=":bee:",
    layout="wide",
)

# OOP brand colors
OOP_TEAL = "#45dcfb"
OOP_PINK = "#fe8cc2"
OOP_YELLOW = "#faf18c"
OOP_NAVY = "#051f38"

CAMPAIGNS_PER_PAGE = 5

# --- Global CSS ---
st.markdown("""
<style>
/* Clean up default Streamlit padding */
.block-container { padding-top: 2rem; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #232940 100%);
    border: 1px solid rgba(69, 220, 251, 0.15);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.metric-card .label {
    font-size: 0.8rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #fafafa;
}
.metric-card .value.teal { color: #45dcfb; }
.metric-card .value.pink { color: #fe8cc2; }
.metric-card .value.yellow { color: #faf18c; }

/* Stat items */
.stat-item {
    background: #1a1f2e;
    border-left: 3px solid #45dcfb;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 0.92rem;
    line-height: 1.5;
}
.stat-item:nth-child(even) { border-left-color: #fe8cc2; }
.stat-item:nth-child(3n) { border-left-color: #faf18c; }

/* Auth warning */
.auth-warning {
    background: linear-gradient(90deg, #ff4b4b, #ff6b6b);
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    font-weight: 600;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
}

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #45dcfb;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 2rem 0 1rem 0;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(69, 220, 251, 0.2);
}

/* Page header */
.page-header {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    color: #888;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: #0e1117;
    border-right: 1px solid #1a1f2e;
}

/* Table styling */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Expander styling */
.streamlit-expanderHeader {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def metric_card(label, value, color=""):
    """Render a styled metric card."""
    color_class = f' {color}' if color else ''
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value{color_class}">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def plotly_dark_layout(fig, **kwargs):
    """Apply consistent dark theme to plotly figures."""
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fafafa", size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc")),
        margin=dict(l=20, r=20, t=50, b=20),
        dragmode=False,
    )
    if "xaxis" not in kwargs:
        base["xaxis"] = dict(gridcolor="rgba(255,255,255,0.05)", fixedrange=True)
    if "yaxis" not in kwargs:
        base["yaxis"] = dict(gridcolor="rgba(255,255,255,0.08)", fixedrange=True)
    base.update(kwargs)
    fig.update_layout(**base)
    return fig


PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}


# --- Auth gate ---
if not check_password():
    st.stop()

# --- Auth expiry warning ---
_auth_days, _auth_expiry = data.load_auth_expiry()
if _auth_days is not None and _auth_days <= 7:
    if _auth_days <= 0:
        _auth_msg = f"Auth EXPIRED ({_auth_expiry}). Run <code>beehiiv-update-auth</code> now."
    else:
        _auth_msg = (
            f"Auth expires in {_auth_days:.0f} day{'s' if _auth_days >= 2 else ''} "
            f"({_auth_expiry}). Run <code>beehiiv-update-auth</code> to refresh."
        )
    st.markdown(f'<div class="auth-warning">Muzni Reminder &mdash; {_auth_msg}</div>',
                unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem 0; text-align:center;">
        <span style="font-size:1.6rem; font-weight:700;">OOP</span>
        <span style="font-size:1rem; color:#888;"> Email Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    page = st.radio(
        "Navigate",
        ["Campaign Overview", "Engagement Detail", "Click Detail", "Newsletter", "Import Audit"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.button("Refresh Data", use_container_width=True):
        data.load_campaign_dashboard.clear()
        data.load_newsletter_dashboard.clear()
        data.load_newsletter_clicks.clear()
        data.load_engagement_detail.clear()
        data.load_click_detail.clear()
        data.load_import_checker.clear()
        data.load_auth_expiry.clear()
        st.rerun()


# ============================================================
# PAGE 1: Campaign Overview
# ============================================================
if page == "Campaign Overview":
    st.markdown('<div class="page-header">Campaign Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Aggregate performance across all email campaigns</div>',
                unsafe_allow_html=True)

    df = data.load_campaign_dashboard()
    if df.empty:
        st.warning("No campaign data found.")
        st.stop()

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Campaigns", len(df))
    with c2:
        metric_card("Avg Open Rate", f"{df['Open Rate %'].mean():.1f}%", "teal")
    with c3:
        metric_card("Avg Click Rate", f"{df['Click Rate %'].mean():.1f}%", "pink")
    with c4:
        metric_card("Avg Delivery Rate", f"{df['Delivery Rate %'].mean():.1f}%", "yellow")

    # --- Paginated charts ---
    chart_df = df[df["Send Date"] != ""].copy()
    if not chart_df.empty:
        chart_df["Send Date"] = pd.to_datetime(chart_df["Send Date"], errors="coerce")
        chart_df = chart_df.dropna(subset=["Send Date"]).sort_values("Send Date")
        chart_df = chart_df.reset_index(drop=True)

        total_campaigns = len(chart_df)
        total_pages = max(1, (total_campaigns + CAMPAIGNS_PER_PAGE - 1) // CAMPAIGNS_PER_PAGE)

        st.markdown("")

        if total_pages > 1:
            pg_cols = st.columns([4, 1])
            with pg_cols[1]:
                chart_page = st.selectbox(
                    "Page", range(1, total_pages + 1),
                    format_func=lambda x: f"Page {x}/{total_pages}",
                    key="chart_page",
                    label_visibility="collapsed",
                )
        else:
            chart_page = 1

        start = (chart_page - 1) * CAMPAIGNS_PER_PAGE
        end = min(start + CAMPAIGNS_PER_PAGE, total_campaigns)
        page_df = chart_df.iloc[start:end].copy()
        page_df["Short Name"] = page_df["Campaign Name"].str[:42]

        # Open/Click rate chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=page_df["Short Name"], y=page_df["Open Rate %"],
            name="Open Rate %",
            marker=dict(color=OOP_TEAL, cornerradius=4),
        ))
        fig.add_trace(go.Bar(
            x=page_df["Short Name"], y=page_df["Click Rate %"],
            name="Click Rate %",
            marker=dict(color=OOP_PINK, cornerradius=4),
        ))
        plotly_dark_layout(fig,
            title=f"Open Rate vs Click Rate ({start+1}–{end} of {total_campaigns})",
            yaxis_title="Rate (%)", barmode="group", height=380,
            xaxis_tickangle=-15,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

        # Volume chart
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=page_df["Short Name"], y=page_df["Recipients"],
            name="Recipients",
            marker=dict(color="rgba(69,220,251,0.3)", line=dict(color=OOP_TEAL, width=1.5), cornerradius=4),
        ))
        fig2.add_trace(go.Bar(
            x=page_df["Short Name"], y=page_df["Delivered"],
            name="Delivered",
            marker=dict(color=OOP_TEAL, cornerradius=4),
        ))
        plotly_dark_layout(fig2,
            title=f"Send Volume ({start+1}–{end} of {total_campaigns})",
            yaxis_title="Count", barmode="overlay", height=350,
            xaxis_tickangle=-15,
        )
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

    # Data table
    st.markdown('<div class="section-header">All Campaigns</div>', unsafe_allow_html=True)
    display_cols = [
        "Campaign Name", "Publication", "Send Date", "Recipients", "Delivered",
        "Delivery Rate %", "Unique Opens", "Open Rate %", "Unique Clicks",
        "Click Rate %", "Unsubscribes", "Spam Reports",
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

    # ===========================================================
    # Interesting Stats
    # ===========================================================
    st.markdown('<div class="section-header">Interesting Stats</div>', unsafe_allow_html=True)

    adf = df.copy()
    if "Send Date" in adf.columns:
        adf["_date"] = pd.to_datetime(adf["Send Date"], errors="coerce")
        adf["_dow"] = adf["_date"].dt.day_name()
        adf["_is_weekend"] = adf["_date"].dt.dayofweek >= 5
    if "Subject Line" in adf.columns:
        adf["_subject_len"] = adf["Subject Line"].str.len()
        adf["_subject_words"] = adf["Subject Line"].str.split().str.len()
        adf["_has_emoji"] = adf["Subject Line"].str.contains(
            r"[^\w\s,.\-!?\'\"()&/:;<>@#$%^*+=\[\]{}|\\~`]", regex=True, na=False
        )
        adf["_has_question"] = adf["Subject Line"].str.contains(r"\?", na=False)
        adf["_has_exclamation"] = adf["Subject Line"].str.contains(r"!", na=False)
        adf["_has_numbers"] = adf["Subject Line"].str.contains(r"\d", na=False)

    adf["_ctor"] = np.where(
        adf["Unique Opens"] > 0,
        (adf["Unique Clicks"] / adf["Unique Opens"] * 100).round(1),
        0,
    )

    stats = []

    # 1. Best open rate
    best_open = adf.loc[adf["Open Rate %"].idxmax()]
    stats.append(
        f"<b>Highest open rate:</b> {best_open['Campaign Name'][:50]} "
        f"at <b>{best_open['Open Rate %']:.1f}%</b>"
    )

    # 2. Best click rate
    best_click = adf.loc[adf["Click Rate %"].idxmax()]
    stats.append(
        f"<b>Highest click rate:</b> {best_click['Campaign Name'][:50]} "
        f"at <b>{best_click['Click Rate %']:.1f}%</b>"
    )

    # 3. Worst open rate
    worst_open = adf.loc[adf["Open Rate %"].idxmin()]
    stats.append(
        f"<b>Lowest open rate:</b> {worst_open['Campaign Name'][:50]} "
        f"at <b>{worst_open['Open Rate %']:.1f}%</b>"
    )

    # 4. Total emails sent
    total_sent = adf["Recipients"].sum()
    total_delivered = adf["Delivered"].sum()
    stats.append(
        f"<b>Total emails sent:</b> {total_sent:,} across {len(adf)} campaigns "
        f"({total_delivered:,} delivered)"
    )

    # 5. Delivery errors
    if "Delivery Errors" in adf.columns:
        total_errors = adf["Delivery Errors"].sum()
        error_rate = (total_errors / total_sent * 100) if total_sent > 0 else 0
        stats.append(
            f"<b>Total delivery errors:</b> {total_errors:,} "
            f"({error_rate:.2f}% of all sends)"
        )

    # 6. Best click-to-open rate
    best_ctor = adf.loc[adf["_ctor"].idxmax()]
    stats.append(
        f"<b>Best click-to-open rate:</b> {best_ctor['Campaign Name'][:50]} "
        f"at <b>{best_ctor['_ctor']:.1f}%</b> (of openers who clicked)"
    )

    # 7. Avg CTOR
    avg_ctor = adf["_ctor"].mean()
    stats.append(f"<b>Avg click-to-open rate:</b> {avg_ctor:.1f}%")

    # 8. Publication comparison
    if "Publication" in adf.columns and adf["Publication"].nunique() > 1:
        pub_stats = adf.groupby("Publication").agg({
            "Open Rate %": "mean", "Click Rate %": "mean", "Recipients": "sum",
        }).round(1)
        parts = []
        for pub_name, r in pub_stats.iterrows():
            parts.append(
                f"{pub_name}: {r['Open Rate %']:.1f}% open, "
                f"{r['Click Rate %']:.1f}% click, {int(r['Recipients']):,} sent"
            )
        stats.append(f"<b>Publication comparison:</b> " + " &bull; ".join(parts))

    # 9-10. Weekend vs weekday
    if "_is_weekend" in adf.columns and adf["_date"].notna().sum() >= 2:
        weekday_df = adf[~adf["_is_weekend"] & adf["_date"].notna()]
        weekend_df = adf[adf["_is_weekend"] & adf["_date"].notna()]
        if not weekday_df.empty and not weekend_df.empty:
            wd_open = weekday_df["Open Rate %"].mean()
            we_open = weekend_df["Open Rate %"].mean()
            winner = "Weekend" if we_open > wd_open else "Weekday"
            diff = abs(we_open - wd_open)
            stats.append(
                f"<b>Weekend vs weekday opens:</b> {winner} campaigns have "
                f"<b>{diff:.1f}pp</b> higher open rates "
                f"(weekday: {wd_open:.1f}%, weekend: {we_open:.1f}%)"
            )
            wd_click = weekday_df["Click Rate %"].mean()
            we_click = weekend_df["Click Rate %"].mean()
            click_winner = "Weekend" if we_click > wd_click else "Weekday"
            click_diff = abs(we_click - wd_click)
            stats.append(
                f"<b>Weekend vs weekday clicks:</b> {click_winner} campaigns have "
                f"<b>{click_diff:.1f}pp</b> higher click rates "
                f"(weekday: {wd_click:.1f}%, weekend: {we_click:.1f}%)"
            )
        elif weekday_df.empty:
            stats.append("<b>All campaigns sent on weekends</b> — no weekday data yet")
        else:
            stats.append("<b>All campaigns sent on weekdays</b> — no weekend data yet")

    # 11. Best day of week
    if "_dow" in adf.columns and adf["_date"].notna().sum() >= 2:
        dow_stats = adf[adf["_date"].notna()].groupby("_dow")["Open Rate %"].mean()
        if len(dow_stats) > 1:
            best_day = dow_stats.idxmax()
            stats.append(
                f"<b>Best day to send:</b> {best_day} "
                f"(avg open rate: {dow_stats[best_day]:.1f}%)"
            )

    # 12. Subject line length
    if "_subject_len" in adf.columns and len(adf) >= 3:
        short = adf[adf["_subject_len"] <= adf["_subject_len"].median()]
        long = adf[adf["_subject_len"] > adf["_subject_len"].median()]
        if not short.empty and not long.empty:
            s_open = short["Open Rate %"].mean()
            l_open = long["Open Rate %"].mean()
            winner = "Shorter" if s_open > l_open else "Longer"
            stats.append(
                f"<b>Subject line length:</b> {winner} subjects perform better "
                f"(short: {s_open:.1f}%, long: {l_open:.1f}%, "
                f"median: {adf['_subject_len'].median():.0f} chars)"
            )

    # 13. Subject word count
    if "_subject_words" in adf.columns and len(adf) >= 3:
        med = adf["_subject_words"].median()
        few = adf[adf["_subject_words"] <= med]
        many = adf[adf["_subject_words"] > med]
        if not few.empty and not many.empty:
            f_open = few["Open Rate %"].mean()
            m_open = many["Open Rate %"].mean()
            winner = "Fewer" if f_open > m_open else "More"
            stats.append(
                f"<b>Subject word count:</b> {winner} words perform better "
                f"(&le;{med:.0f} words: {f_open:.1f}%, "
                f"&gt;{med:.0f} words: {m_open:.1f}%)"
            )

    # 14. Emoji in subject
    if "_has_emoji" in adf.columns:
        w = adf[adf["_has_emoji"]]
        wo = adf[~adf["_has_emoji"]]
        if not w.empty and not wo.empty:
            verdict = "higher" if w["Open Rate %"].mean() > wo["Open Rate %"].mean() else "lower"
            stats.append(
                f"<b>Emojis in subject:</b> Campaigns with emojis have <b>{verdict}</b> "
                f"open rates ({w['Open Rate %'].mean():.1f}% vs {wo['Open Rate %'].mean():.1f}%)"
            )

    # 15. Question marks
    if "_has_question" in adf.columns:
        w = adf[adf["_has_question"]]
        wo = adf[~adf["_has_question"]]
        if not w.empty and not wo.empty:
            verdict = "higher" if w["Open Rate %"].mean() > wo["Open Rate %"].mean() else "lower"
            stats.append(
                f"<b>Questions in subject:</b> Subjects with '?' have <b>{verdict}</b> "
                f"open rates ({w['Open Rate %'].mean():.1f}% vs {wo['Open Rate %'].mean():.1f}%)"
            )

    # 16. Exclamation marks
    if "_has_exclamation" in adf.columns:
        w = adf[adf["_has_exclamation"]]
        wo = adf[~adf["_has_exclamation"]]
        if not w.empty and not wo.empty:
            verdict = "higher" if w["Open Rate %"].mean() > wo["Open Rate %"].mean() else "lower"
            stats.append(
                f"<b>Exclamation marks:</b> Subjects with '!' have <b>{verdict}</b> "
                f"open rates ({w['Open Rate %'].mean():.1f}% vs {wo['Open Rate %'].mean():.1f}%)"
            )

    # 17. Most unsubscribes
    if "Unsubscribes" in adf.columns:
        most_unsubs = adf.loc[adf["Unsubscribes"].idxmax()]
        total_unsubs = adf["Unsubscribes"].sum()
        stats.append(
            f"<b>Total unsubscribes:</b> {total_unsubs} across all campaigns. "
            f"Most: {most_unsubs['Campaign Name'][:50]} ({int(most_unsubs['Unsubscribes'])})"
        )

    # 18. Audience size effect
    if len(adf) >= 3:
        small = adf[adf["Recipients"] <= adf["Recipients"].median()]
        large = adf[adf["Recipients"] > adf["Recipients"].median()]
        if not small.empty and not large.empty:
            s_open = small["Open Rate %"].mean()
            l_open = large["Open Rate %"].mean()
            winner = "Smaller" if s_open > l_open else "Larger"
            stats.append(
                f"<b>Audience size effect:</b> {winner} audiences have higher open rates "
                f"(small: {s_open:.1f}%, large: {l_open:.1f}%, "
                f"median: {adf['Recipients'].median():.0f})"
            )

    # 19. Numbers in subject
    if "_has_numbers" in adf.columns:
        w = adf[adf["_has_numbers"]]
        wo = adf[~adf["_has_numbers"]]
        if not w.empty and not wo.empty:
            verdict = "higher" if w["Open Rate %"].mean() > wo["Open Rate %"].mean() else "lower"
            stats.append(
                f"<b>Numbers in subject:</b> Subjects with numbers have <b>{verdict}</b> "
                f"open rates ({w['Open Rate %'].mean():.1f}% vs {wo['Open Rate %'].mean():.1f}%)"
            )

    # 20. Spam rate
    if "Spam Reports" in adf.columns:
        total_spam = adf["Spam Reports"].sum()
        spam_rate = (total_spam / total_delivered * 100) if total_delivered > 0 else 0
        stats.append(
            f"<b>Spam report rate:</b> {total_spam} total ({spam_rate:.3f}% of delivered)"
        )

    # Render as styled cards
    for stat in stats:
        st.markdown(f'<div class="stat-item">{stat}</div>', unsafe_allow_html=True)


# ============================================================
# PAGE 4: Newsletter
# ============================================================
elif page == "Newsletter":
    st.markdown('<div class="page-header">Newsletter Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Out-Of-Pocket Health Newsletter — 30K+ subscribers</div>',
                unsafe_allow_html=True)

    df = data.load_newsletter_dashboard()
    if df.empty:
        st.warning("No newsletter data found. Dashboard may not have run yet.")
        st.stop()

    click_df = data.load_newsletter_clicks()

    # --- Campaign Selector ---
    campaign_options = ["All Campaigns"] + df["Campaign Name"].tolist()
    selected_campaign = st.selectbox("Select Campaign", campaign_options, key="nl_campaign")

    is_all = selected_campaign == "All Campaigns"

    if is_all:
        # ===================== ALL CAMPAIGNS VIEW =====================
        # KPI cards — row 1
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            metric_card("Campaigns", len(df))
        with c2:
            metric_card("Avg Open Rate", f"{df['Open Rate %'].mean():.1f}%", "teal")
        with c3:
            metric_card("Avg Click Rate", f"{df['Click Rate %'].mean():.1f}%", "pink")
        with c4:
            metric_card("Avg CTOR", f"{df['CTOR %'].mean():.1f}%", "yellow")
        with c5:
            metric_card("Avg Unsub Rate", f"{df['Unsub Rate %'].mean():.2f}%")

        # KPI cards — row 2
        st.markdown("")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Total Sent", f"{df['Sent'].sum():,}", "teal")
        with c2:
            metric_card("Total Delivered", f"{df['Delivered'].sum():,}")
        with c3:
            metric_card("Total Opens", f"{df['Total Opens'].sum():,}", "pink")
        with c4:
            metric_card("Total Unsubs", f"{df['Unsubscribes'].sum():,}", "yellow")

        # --- Performance Trends ---
        chart_df = df[df["Send Date"] != ""].copy()
        if not chart_df.empty:
            chart_df["Send Date"] = pd.to_datetime(chart_df["Send Date"], errors="coerce")
            chart_df = chart_df.dropna(subset=["Send Date"]).sort_values("Send Date")

            st.markdown('<div class="section-header">Performance Trends</div>', unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_df["Send Date"], y=chart_df["Open Rate %"],
                name="Open Rate %", mode="lines+markers",
                line=dict(color=OOP_TEAL, width=2.5), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=chart_df["Send Date"], y=chart_df["Click Rate %"],
                name="Click Rate %", mode="lines+markers",
                line=dict(color=OOP_PINK, width=2.5), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=chart_df["Send Date"], y=chart_df["CTOR %"],
                name="CTOR %", mode="lines+markers",
                line=dict(color=OOP_YELLOW, width=2, dash="dot"), marker=dict(size=6),
            ))
            plotly_dark_layout(fig,
                title="Open Rate / Click Rate / CTOR Over Time",
                yaxis_title="Rate (%)", height=400,
            )
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

            # Re-read depth
            if chart_df["Unique Opens"].sum() > 0:
                chart_df["Opens per Reader"] = (chart_df["Total Opens"] / chart_df["Unique Opens"]).round(2)
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=chart_df["Campaign Name"].str[:40], y=chart_df["Unique Opens"],
                    name="Unique Opens", marker=dict(color=OOP_TEAL, cornerradius=4),
                ))
                fig2.add_trace(go.Scatter(
                    x=chart_df["Campaign Name"].str[:40], y=chart_df["Opens per Reader"],
                    name="Opens per Reader", yaxis="y2", mode="lines+markers",
                    line=dict(color=OOP_YELLOW, width=2), marker=dict(size=7),
                ))
                plotly_dark_layout(fig2,
                    title="Unique Opens & Re-Read Depth", height=380, xaxis_tickangle=-20,
                    yaxis=dict(title="Unique Opens", gridcolor="rgba(255,255,255,0.05)", fixedrange=True),
                    yaxis2=dict(title="Opens / Reader", overlaying="y", side="right",
                                gridcolor="rgba(0,0,0,0)", fixedrange=True),
                )
                st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

            # Unsub trend
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=chart_df["Campaign Name"].str[:40], y=chart_df["Unsubscribes"],
                name="Unsubscribes", marker=dict(color=OOP_PINK, cornerradius=4),
            ))
            fig3.add_trace(go.Scatter(
                x=chart_df["Campaign Name"].str[:40], y=chart_df["Unsub Rate %"],
                name="Unsub Rate %", yaxis="y2", mode="lines+markers",
                line=dict(color=OOP_YELLOW, width=2), marker=dict(size=7),
            ))
            plotly_dark_layout(fig3,
                title="Unsubscribes by Campaign", height=350, xaxis_tickangle=-20,
                yaxis=dict(title="Count", gridcolor="rgba(255,255,255,0.05)", fixedrange=True),
                yaxis2=dict(title="Unsub Rate %", overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)", fixedrange=True),
            )
            st.plotly_chart(fig3, use_container_width=True, config=PLOTLY_CONFIG)

        # All campaigns table
        st.markdown('<div class="section-header">All Newsletter Campaigns</div>', unsafe_allow_html=True)
        display_cols = [
            "Campaign Name", "Send Date", "Sent", "Delivered", "Delivery Rate %",
            "Unique Opens", "Open Rate %", "Unique Clicks", "Click Rate %",
            "CTOR %", "Unsubscribes", "Unsub Rate %", "Spam Reports",
        ]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

        # --- Insights ---
        st.markdown('<div class="section-header">Newsletter Insights</div>', unsafe_allow_html=True)
        nstats = []

        best_open = df.loc[df["Open Rate %"].idxmax()]
        nstats.append(
            f"<b>Highest open rate:</b> {best_open['Campaign Name'][:55]} "
            f"at <b>{best_open['Open Rate %']:.1f}%</b>"
        )
        worst_open = df.loc[df["Open Rate %"].idxmin()]
        nstats.append(
            f"<b>Lowest open rate:</b> {worst_open['Campaign Name'][:55]} "
            f"at <b>{worst_open['Open Rate %']:.1f}%</b>"
        )
        best_click = df.loc[df["Click Rate %"].idxmax()]
        nstats.append(
            f"<b>Highest click rate:</b> {best_click['Campaign Name'][:55]} "
            f"at <b>{best_click['Click Rate %']:.1f}%</b> "
            f"(CTOR: {best_click['CTOR %']:.1f}%)"
        )

        total_sent = df["Sent"].sum()
        total_delivered = df["Delivered"].sum()
        overall_delivery = round(total_delivered / total_sent * 100, 2) if total_sent > 0 else 0
        nstats.append(
            f"<b>Delivery health:</b> {total_delivered:,} / {total_sent:,} delivered "
            f"(<b>{overall_delivery}%</b> overall)"
        )

        if df["Unique Opens"].sum() > 0:
            avg_reads = df["Total Opens"].sum() / df["Unique Opens"].sum()
            nstats.append(
                f"<b>Avg reads per opener:</b> {avg_reads:.2f}x "
                f"(readers re-open newsletters ~{avg_reads - 1:.1f} extra times on average)"
            )

        most_unsub = df.loc[df["Unsubscribes"].idxmax()]
        nstats.append(
            f"<b>Most unsubscribes:</b> {most_unsub['Campaign Name'][:55]} "
            f"({int(most_unsub['Unsubscribes'])} unsubs, {most_unsub['Unsub Rate %']:.2f}%)"
        )
        nstats.append(
            f"<b>Total unsubscribes:</b> {df['Unsubscribes'].sum():,} across {len(df)} newsletters "
            f"&bull; Spam reports: {df['Spam Reports'].sum()}"
        )

        if "Subject Line" in df.columns and len(df) >= 3:
            df["_slen"] = df["Subject Line"].str.len()
            short = df[df["_slen"] <= df["_slen"].median()]
            long = df[df["_slen"] > df["_slen"].median()]
            if not short.empty and not long.empty:
                winner = "Shorter" if short["Open Rate %"].mean() > long["Open Rate %"].mean() else "Longer"
                nstats.append(
                    f"<b>Subject line length:</b> {winner} subjects perform better "
                    f"(short: {short['Open Rate %'].mean():.1f}%, long: {long['Open Rate %'].mean():.1f}%, "
                    f"median: {df['_slen'].median():.0f} chars)"
                )

        for s in nstats:
            st.markdown(f'<div class="stat-item">{s}</div>', unsafe_allow_html=True)

    else:
        # ===================== SINGLE CAMPAIGN VIEW =====================
        row = df[df["Campaign Name"] == selected_campaign].iloc[0]

        # KPI cards
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            metric_card("Sent", f"{int(row['Sent']):,}")
        with c2:
            metric_card("Open Rate", f"{row['Open Rate %']:.1f}%", "teal")
        with c3:
            metric_card("Click Rate", f"{row['Click Rate %']:.1f}%", "pink")
        with c4:
            metric_card("CTOR", f"{row['CTOR %']:.1f}%", "yellow")
        with c5:
            metric_card("Unsub Rate", f"{row['Unsub Rate %']:.2f}%")

        st.markdown("")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            metric_card("Delivered", f"{int(row['Delivered']):,}", "teal")
        with c2:
            metric_card("Delivery Rate", f"{row['Delivery Rate %']:.1f}%")
        with c3:
            metric_card("Unique Opens", f"{int(row['Unique Opens']):,}", "pink")
        with c4:
            metric_card("Total Opens", f"{int(row['Total Opens']):,}")
        with c5:
            reads_per = round(row["Total Opens"] / row["Unique Opens"], 2) if row["Unique Opens"] > 0 else 0
            metric_card("Opens / Reader", f"{reads_per}x", "yellow")

        st.markdown("")
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Unique Clicks", f"{int(row['Unique Clicks']):,}", "teal")
        with c2:
            metric_card("Unsubscribes", f"{int(row['Unsubscribes']):,}", "pink")
        with c3:
            metric_card("Spam Reports", f"{int(row['Spam Reports']):,}")

        # Engagement pie chart
        st.markdown("")
        opened_not_clicked = int(row["Unique Opens"]) - int(row["Unique Clicks"])
        not_opened = int(row["Delivered"]) - int(row["Unique Opens"])
        not_delivered = int(row["Sent"]) - int(row["Delivered"])
        pie_labels = ["Clicked", "Opened Only", "Not Opened", "Not Delivered"]
        pie_values = [int(row["Unique Clicks"]), max(0, opened_not_clicked),
                      max(0, not_opened), max(0, not_delivered)]
        if sum(pie_values) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=pie_labels, values=pie_values,
                marker=dict(colors=[OOP_TEAL, OOP_PINK, OOP_YELLOW, "#555"]),
                hole=0.45, textinfo="percent+label", textfont=dict(size=13),
            )])
            plotly_dark_layout(fig, title="Engagement Breakdown", height=380)
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

        # Subject line and send date info
        if row.get("Subject Line"):
            st.markdown(f'<div class="stat-item"><b>Subject Line:</b> {row["Subject Line"]}</div>',
                        unsafe_allow_html=True)
        if row.get("Send Date"):
            st.markdown(f'<div class="stat-item"><b>Send Date:</b> {row["Send Date"]}</div>',
                        unsafe_allow_html=True)

        # Click detail for this campaign
        if not click_df.empty:
            campaign_clicks = click_df[click_df["Campaign Name"] == selected_campaign].copy()
            if not campaign_clicks.empty:
                campaign_clicks = campaign_clicks.sort_values("Unique Clicks", ascending=False)

                st.markdown('<div class="section-header">Link Performance</div>',
                            unsafe_allow_html=True)

                top = campaign_clicks.head(15).copy()
                top["URL (short)"] = top["URL"].str[:65]
                fig_c = go.Figure(go.Bar(
                    x=top["Unique Clicks"], y=top["URL (short)"],
                    orientation="h",
                    marker=dict(
                        color=top["Unique Clicks"],
                        colorscale=[[0, OOP_NAVY], [0.5, OOP_TEAL], [1, OOP_PINK]],
                        cornerradius=4,
                    ),
                ))
                plotly_dark_layout(fig_c,
                    title="Links by Unique Clicks", height=420,
                    yaxis=dict(autorange="reversed", gridcolor="rgba(255,255,255,0.03)",
                               fixedrange=True),
                )
                st.plotly_chart(fig_c, use_container_width=True, config=PLOTLY_CONFIG)

                st.dataframe(campaign_clicks[["URL", "Unique Clicks", "Total Clicks"]],
                             use_container_width=True, hide_index=True)
            else:
                st.info("No click data for this campaign.")

    # --- Link Search (always visible) ---
    st.markdown('<div class="section-header">Link Search</div>', unsafe_allow_html=True)
    st.caption("Search for a sponsor link or any URL to see how it performed across newsletters")
    link_query = st.text_input("Search URL", placeholder="e.g. ursahealth.com or sponsor-name",
                               key="nl_link_search", label_visibility="collapsed")
    if link_query and not click_df.empty:
        matches = click_df[click_df["URL"].str.contains(link_query, case=False, na=False)].copy()
        if not matches.empty:
            matches = matches.sort_values("Unique Clicks", ascending=False)
            total_unique = matches["Unique Clicks"].sum()
            total_all = matches["Total Clicks"].sum()
            num_campaigns = matches["Campaign Name"].nunique()

            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card("Total Unique Clicks", f"{total_unique:,}", "teal")
            with c2:
                metric_card("Total Clicks", f"{total_all:,}", "pink")
            with c3:
                metric_card("Appeared In", f"{num_campaigns} newsletter{'s' if num_campaigns != 1 else ''}")

            st.dataframe(matches[["Campaign Name", "URL", "Unique Clicks", "Total Clicks"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info(f"No links matching '{link_query}' found.")


# ============================================================
# PAGE 3: Engagement Detail
# ============================================================
elif page == "Engagement Detail":
    st.markdown('<div class="page-header">Engagement Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Per-subscriber engagement breakdown by campaign</div>',
                unsafe_allow_html=True)

    df = data.load_engagement_detail()
    if df.empty:
        st.warning("No engagement data found. Internal API auth may be expired.")
        st.stop()

    if len(df) == 1 and "AUTH EXPIRED" in str(df.iloc[0, 0]):
        st.error("Internal API auth expired. Run `beehiiv-update-auth` to refresh.")
        st.stop()

    campaigns = df["Campaign Name"].tolist()
    selected = st.selectbox("Select Campaign", campaigns, label_visibility="collapsed",
                            key="eng_campaign")

    matched = df[df["Campaign Name"] == selected]
    if matched.empty:
        st.warning(f"Campaign '{selected}' not found. Try refreshing.")
        st.stop()
    row = matched.iloc[0]

    # Metric cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Clicked", int(row.get("Opened & Clicked (count)", 0)), "teal")
    with c2:
        metric_card("Opened Only", int(row.get("Opened Only (count)", 0)), "pink")
    with c3:
        metric_card("Not Opened", int(row.get("Not Opened - FOLLOW UP (count)", 0)), "yellow")
    with c4:
        metric_card("Not Delivered", int(row.get("Not Delivered (count)", 0)))

    st.markdown("")

    # Pie chart
    labels = ["Clicked", "Opened Only", "Not Opened", "Not Delivered"]
    values = [
        row.get("Opened & Clicked (count)", 0),
        row.get("Opened Only (count)", 0),
        row.get("Not Opened - FOLLOW UP (count)", 0),
        row.get("Not Delivered (count)", 0),
    ]
    if sum(values) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values,
            marker=dict(colors=[OOP_TEAL, OOP_PINK, OOP_YELLOW, "#555"]),
            hole=0.45,
            textinfo="percent+label",
            textfont=dict(size=13),
        )])
        plotly_dark_layout(fig, title="Engagement Breakdown", height=380)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Email lists
    def _parse_emails(cell_value):
        if not cell_value or cell_value == "None" or pd.isna(cell_value):
            return []
        return [e.strip() for e in str(cell_value).split(",") if e.strip()]

    st.markdown('<div class="section-header">Email Lists</div>', unsafe_allow_html=True)

    with st.expander(f"Opened & Clicked ({row.get('Opened & Clicked (count)', 0)})"):
        emails = _parse_emails(row.get("Opened & Clicked (emails)", ""))
        if emails:
            st.text("\n".join(emails))
        else:
            st.caption("No emails")

    with st.expander(f"Opened Only ({row.get('Opened Only (count)', 0)})"):
        emails = _parse_emails(row.get("Opened Only (emails)", ""))
        if emails:
            st.text("\n".join(emails))
        else:
            st.caption("No emails")

    with st.expander(f"Not Opened ({row.get('Not Opened - FOLLOW UP (count)', 0)})"):
        emails = _parse_emails(row.get("Not Opened - FOLLOW UP (emails)", ""))
        if emails:
            st.text("\n".join(emails))
        else:
            st.caption("No emails")

    with st.expander(f"Not Delivered ({row.get('Not Delivered (count)', 0)})"):
        emails = _parse_emails(row.get("Not Delivered (emails)", ""))
        if emails:
            st.text("\n".join(emails))
        else:
            st.caption("No emails")

    current_tag = row.get("Tag Name", "")
    if current_tag:
        st.caption(f"Segment: {current_tag}")


# ============================================================
# PAGE 3: Click Detail
# ============================================================
elif page == "Click Detail":
    st.markdown('<div class="page-header">Click Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Per-URL click breakdown across campaigns</div>',
                unsafe_allow_html=True)

    df = data.load_click_detail()
    if df.empty:
        st.warning("No click data found.")
        st.stop()

    campaigns = ["All"] + sorted(df["Campaign Name"].unique().tolist())
    selected_campaign = st.selectbox("Filter by Campaign", campaigns,
                                     label_visibility="collapsed", key="click_campaign")

    filtered = df if selected_campaign == "All" else df[df["Campaign Name"] == selected_campaign]

    if not filtered.empty:
        top_urls = filtered.nlargest(15, "Unique Clicks").copy()
        top_urls["URL (short)"] = top_urls["URL"].str[:55]

        fig = go.Figure(go.Bar(
            x=top_urls["Unique Clicks"],
            y=top_urls["URL (short)"],
            orientation="h",
            marker=dict(
                color=top_urls["Unique Clicks"],
                colorscale=[[0, OOP_NAVY], [0.5, OOP_TEAL], [1, OOP_PINK]],
                cornerradius=4,
            ),
        ))
        plotly_dark_layout(fig,
            title="Top URLs by Unique Clicks",
            height=480,
            yaxis=dict(autorange="reversed", gridcolor="rgba(255,255,255,0.03)", fixedrange=True),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown('<div class="section-header">All Click Data</div>', unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)


# ============================================================
# PAGE 4: Import Audit
# ============================================================
elif page == "Import Audit":
    st.markdown('<div class="page-header">Import Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Beehiiv import verification results</div>',
                unsafe_allow_html=True)

    df = data.load_import_checker()
    if df.empty:
        st.warning("No import audit data found.")
        st.stop()

    total_imported = df["Total Imported"].sum()
    total_missing = df["Missing Number"].sum()
    success_rate = ((total_imported - total_missing) / total_imported * 100) if total_imported > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Total Imports", len(df))
    with c2:
        metric_card("Contacts Imported", f"{total_imported:,}", "teal")
    with c3:
        metric_card("Success Rate", f"{success_rate:.1f}%", "pink")

    st.markdown("")

    if not df.empty:
        chart_df = df.copy()
        chart_df["Successful"] = chart_df["Total Imported"] - chart_df["Missing Number"]
        chart_df["Tag (short)"] = chart_df["Tag Type"].str[:35]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=chart_df["Tag (short)"], y=chart_df["Successful"],
            name="Successful",
            marker=dict(color=OOP_TEAL, cornerradius=4),
        ))
        fig.add_trace(go.Bar(
            x=chart_df["Tag (short)"], y=chart_df["Missing Number"],
            name="Missing",
            marker=dict(color=OOP_PINK, cornerradius=4),
        ))
        plotly_dark_layout(fig,
            title="Import Results by Tag/Segment",
            barmode="stack", height=380, xaxis_tickangle=-25,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown('<div class="section-header">All Import Checks</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">Missing Email Details</div>', unsafe_allow_html=True)
    for _, row in df.iterrows():
        missing_str = row.get("Missing Email IDs", "None")
        if missing_str and missing_str != "None":
            with st.expander(f"{row['Tag Type']} — {row['Missing Number']} missing"):
                emails = [e.strip() for e in missing_str.split(",") if e.strip()]
                st.text("\n".join(emails))
