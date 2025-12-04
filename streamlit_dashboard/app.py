# streamlit_dashboard/app.py
import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px

# import your existing modules (adjust paths if needed)
# api.fetch_all_leagues() must return a list of matches with:
# {"title": "...", "market": "1X2", "bookmakers_odds": {"BookA": 1.9, ...}}
from modules import api as odds_api
from modules import engine as value_engine

st.set_page_config(page_title="Hummingbird Dashboard (Live)", layout="wide")

# --- Sidebar settings ---
st.sidebar.title("Hummingbird — Live Dashboard")
REFRESH_SECONDS = st.sidebar.number_input("Auto-refresh (seconds)", min_value=5, max_value=300, value=15, step=5)
SHOW_ONLY_SIGNALS = st.sidebar.checkbox("Show only value signals", value=False)
TOP_N = st.sidebar.slider("Top N value signals to show", 1, 50, 20)

# Optional filters
league_filter = st.sidebar.multiselect("Filter leagues (empty = all)", options=[
    "soccer_epl",
    "soccer_uefa_champs_league",
    "soccer_france_ligue_one",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga"
], default=[])

st.sidebar.markdown("---")
st.sidebar.caption("Do not commit your API keys. Use Streamlit Secrets or env variables.")

# --- Header ---
col1, col2 = st.columns([3,1])
col1.title("🟢 Hummingbird Live Odds Dashboard")
col2.markdown("**Status:** Live")
col2.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# --- Helper: fetch data (cached to avoid over-calling API) ---
@st.cache_data(ttl=REFRESH_SECONDS)
def fetch_data():
    try:
        data = odds_api.fetch_all_leagues()  # uses ODDS_API_KEY internally
        return data
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return []

# --- Fetch & filter ---
data = fetch_data()

# Optionally filter by league
if league_filter:
    data = [m for m in data if m.get("league") in league_filter]

# --- Build a DataFrame for display ---
def build_display_df(items):
    rows = []
    for m in items:
        title = m.get("title")
        league = m.get("league", "unknown")
        odds = m.get("bookmakers_odds", {})
        # Flatten top few bookmakers
        row = {"match": title, "league": league}
        for b, odd in odds.items():
            row[f"odds_{b}"] = odd
        rows.append(row)
    return pd.DataFrame(rows)

df_display = build_display_df(data)

# Layout: Left column = live table + filters, Right column = Signals + charts
left, right = st.columns([2, 1])

with left:
    st.subheader("📡 Live Matches & Bookmaker Odds")
    if df_display.empty:
        st.info("No live data. Check your API key and rate limits.")
    else:
        st.dataframe(df_display, height=450)

with right:
    st.subheader("🧠 Value Signals (Top)")
    signals = []
    for match in data:
        odds_dict = match.get("bookmakers_odds", {})
        if not odds_dict:
            continue
        result = value_engine.detect_value(odds_dict)
        if not result:
            continue
        # best row (highest value_edge)
        best_row = result["results"].iloc[0]
        signal = {
            "match": match.get("title"),
            "league": match.get("league"),
            "best_book": best_row["book"],
            "best_odds": float(best_row["odds"]),
            "value_edge": float(best_row["value_edge"]),
            "signal": best_row["value_signal"],
            "true_odds": float(result["true_odds"])
        }
        signals.append(signal)

    if not signals:
        st.info("No value detected right now.")
    else:
        df_signals = pd.DataFrame(signals).sort_values("value_edge", ascending=False)
        if SHOW_ONLY_SIGNALS:
            st.dataframe(df_signals[df_signals["signal"] != "NONE"].head(TOP_N))
        else:
            st.dataframe(df_signals.head(TOP_N))

    # mini chart: distribution of value edges
    if signals:
        fig = px.histogram(pd.DataFrame(signals), x="value_edge", nbins=20, title="Value edge distribution")
        st.plotly_chart(fig, use_container_width=True)

# --- Match detail explorer ---
st.markdown("---")
st.subheader("🔎 Match details")
match_select = st.selectbox("Choose match", options=[m["title"] for m in data] if data else [])
if match_select:
    match_obj = next((m for m in data if m["title"] == match_select), None)
    if match_obj:
        st.markdown(f"**{match_obj.get('title')}** — League: {match_obj.get('league')}")
        odds_df = pd.DataFrame(list(match_obj.get("bookmakers_odds", {}).items()), columns=["bookmaker","odds"])
        st.table(odds_df)

# --- Auto refresh indicator ---
st.experimental_singleton.clear()  # ensures cache respects TTL
st_autorefresh = st.experimental_rerun if False else None

# We can't block; just advise user to enable auto-refresh on hosting:
st.markdown(f"Auto-refresh every **{REFRESH_SECONDS}** sec (server-side cache TTL).")

