"""Google Sheets data loading for the Beehiiv dashboard."""

from datetime import datetime, timezone

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


def _get_client():
    """Get authenticated gspread client using domain-wide delegation."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Support both local (file path) and cloud (inline JSON via [gcp_service_account])
    if "google_credentials_path" in st.secrets:
        creds = Credentials.from_service_account_file(
            st.secrets["google_credentials_path"], scopes=scopes
        )
    else:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=scopes
        )
    delegated = creds.with_subject(st.secrets["impersonate_email"])
    return gspread.authorize(delegated)


@st.cache_data(ttl=300)
def load_campaign_dashboard():
    """Load Campaign Dashboard tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(0)  # "Campaign Dashboard"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    # Parse numeric columns
    for col in ["Recipients", "Delivered", "Delivery Errors", "Unique Opens",
                 "Unique Clicks", "Unsubscribes", "Spam Reports"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Parse percentage columns (strip % sign)
    for col in ["Delivery Rate %", "Open Rate %", "Click Rate %"]:
        if col in df.columns:
            df[col] = df[col].str.replace("%", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


@st.cache_data(ttl=300)
def load_engagement_detail():
    """Load Engagement Detail tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(549973242)  # "Engagement Detail"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    # Parse count columns
    for col in ["Opened & Clicked (count)", "Opened Only (count)",
                 "Not Opened - FOLLOW UP (count)", "Not Delivered (count)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


@st.cache_data(ttl=300)
def load_click_detail():
    """Load Click Detail tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(1560513873)  # "Click Detail"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    for col in ["Unique Clicks", "Total Clicks"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "Click-Through Rate %" in df.columns:
        df["Click-Through Rate %"] = (
            df["Click-Through Rate %"].str.replace("%", "").str.strip()
        )
        df["Click-Through Rate %"] = pd.to_numeric(
            df["Click-Through Rate %"], errors="coerce"
        ).fillna(0)

    return df


@st.cache_data(ttl=300)
def load_import_checker():
    """Load Check Master tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["import_checker_sheet_id"])
    ws = sh.get_worksheet_by_id(0)  # "Check Master"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    # Normalize column names (sheet has trailing spaces and different naming)
    col_map = {}
    for col in df.columns:
        stripped = col.strip().lower()
        if "tag" in stripped and "type" in stripped:
            col_map[col] = "Tag Type"
        elif stripped == "total rows in csv":
            col_map[col] = "Total Rows in CSV"
        elif stripped == "total imported":
            col_map[col] = "Total Imported"
        elif "missing" in stripped and "number" in stripped:
            col_map[col] = "Missing Number"
        elif "missing" in stripped and "email" in stripped:
            col_map[col] = "Missing Email IDs"
        elif "duplicate" in stripped:
            col_map[col] = "Duplicates Found"
    df = df.rename(columns=col_map)

    for col in ["Total Imported", "Missing Number"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


@st.cache_data(ttl=300)
def load_newsletter_dashboard():
    """Load Newsletter Dashboard tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(1533589416)  # "Newsletter Dashboard"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    for col in ["Sent", "Delivered", "Unique Opens", "Total Opens",
                 "Unique Clicks", "Unsubscribes", "Spam Reports"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["Delivery Rate %", "Open Rate %", "Click Rate %",
                 "CTOR %", "Unsub Rate %"]:
        if col in df.columns:
            df[col] = df[col].str.replace("%", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


@st.cache_data(ttl=300)
def load_newsletter_clicks():
    """Load Newsletter Click Detail tab into a DataFrame."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(1801678154)  # "Newsletter Click Detail"
    rows = ws.get_all_values()
    if len(rows) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])

    for col in ["Unique Clicks", "Total Clicks", "Unique Verified Clicks"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["Click Rate %", "Verified Click Rate %"]:
        if col in df.columns:
            df[col] = df[col].str.replace("%", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


@st.cache_data(ttl=300)
def load_auth_expiry():
    """Read JWT auth expiry date from cell P1 of Campaign Dashboard.

    Returns (days_left, expiry_date_str) or (None, None) if not set.
    """
    try:
        gc = _get_client()
        sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
        ws = sh.get_worksheet_by_id(0)  # "Campaign Dashboard"
        expiry_str = ws.acell("P1").value
        if not expiry_str or not expiry_str.strip():
            return None, None
        expiry_date = datetime.strptime(expiry_str.strip(), "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(tz=timezone.utc)
        days_left = (expiry_date - now).total_seconds() / 86400
        return days_left, expiry_str.strip()
    except Exception:
        return None, None


def update_segment_name(campaign_name, segment_name):
    """Write segment name to col L of Engagement Detail for a specific campaign."""
    gc = _get_client()
    sh = gc.open_by_key(st.secrets["dashboard_sheet_id"])
    ws = sh.get_worksheet_by_id(549973242)  # "Engagement Detail"
    rows = ws.get_all_values()

    # Find the row for this campaign (col A = campaign name)
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if row[0] == campaign_name:
            # Col L = column 12
            ws.update_cell(i + 1, 12, segment_name)
            # Clear cache so next load reflects the change
            load_engagement_detail.clear()
            return True
    return False
