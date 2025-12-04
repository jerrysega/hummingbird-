import streamlit as st
import pandas as pd
import time
from engine import detect_value
from modules.api import fetch_all_leagues

st.set_page_config(page_title="Hummingbird Dashboard", layout="wide")

st.title("🟢 Hummingbird Live Odds Dashboard")
st.markdown("Live monitoring + value detection model")

# Sidebar refresh rate
refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 5, 60, 10)

# Placeholder containers
live_container = st.empty()
signals_container = st.container()

while True:
    with live_container:
        st.subheader("📡 Live Odds Fetching")
        data = fetch_all_leagues()

        if data is None or len(data) == 0:
            st.warning("No data fetched.")
            time.sleep(refresh_rate)
            continue

        # Display fetched matches
        st.dataframe(pd.DataFrame(data))

        st.subheader("🧠 Value Detection")
        all_signals = []

        for match in data:
            try:
                odds = match["bookmakers_odds"]  # dict {bookmaker: odds}
                value = detect_value(odds)

                if value and not value["results"].empty:
                    best = value["results"].iloc[0]

                    signal = {
                        "match": match["title"],
                        "market": match["market"],
                        "true_odds": round(value["true_odds"], 2),
                        "best_book": best["book"],
                        "best_odds": best["odds"],
                        "value_edge": round(best["value_edge"], 2),
                        "signal": best["value_signal"],
                    }

                    all_signals.append(signal)
            except:
                continue

        df_signals = pd.DataFrame(all_signals)

        if not df_signals.empty:
            strong = df_signals[df_signals["signal"] == "STRONG"]
            medium = df_signals[df_signals["signal"] == "MEDIUM"]

            st.success(f"STRONG signals: {len(strong)} | MEDIUM: {len(medium)}")

            st.dataframe(df_signals.sort_values("value_edge", ascending=False))
        else:
            st.info("No value detected yet.")

    time.sleep(refresh_rate)
