import time
import pandas as pd
import numpy as np

# ----------------------------
# VALUE DETECTION ENGINE
# ----------------------------

def implied_prob(odds):
    """Convert decimal odds → implied probability."""
    return 1 / odds if odds > 0 else 0

def fair_odds(implied):
    """Convert implied probability → fair odds."""
    if implied == 0:
        return 0
    return 1 / implied

def detect_value(bookmaker_odds, sharp_weight=0.65, move_weight=0.35):
    """
    bookmaker_odds = {
        "pinnacle": 1.85,
        "bet365": 1.80,
        "williamhill": 1.83,
    }
    """
    df = pd.DataFrame([
        {"book": k, "odds": v, "prob": implied_prob(v)}
        for k, v in bookmaker_odds.items()
        if v not in [None, 0]
    ])

    if df.empty:
        return None

    # Market mean
    market_prob = df["prob"].mean()

    # Market sharpest book → assumed Pinnacle or best priced
    sharpest = df.loc[df["prob"].idxmin()]  # lowest implied prob = highest odds

    # Compute fair probability
    true_prob = (sharp_weight * sharpest["prob"]) + (move_weight * market_prob)
    true_odds = fair_odds(true_prob)

    # Compare each bookmaker → calculate value edge
    df["true_odds"] = true_odds
    df["value_edge"] = df["odds"] - df["true_odds"]

    df["value_signal"] = df["value_edge"].apply(
        lambda x: "STRONG" if x >= 0.20 else ("MEDIUM" if x >= 0.10 else "NONE")
    )

    return {
        "true_prob": true_prob,
        "true_odds": true_odds,
        "results": df.sort_values("value_edge", ascending=False)
    }
