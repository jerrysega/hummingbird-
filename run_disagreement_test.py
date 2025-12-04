from data.odds_monitor import OddsMonitor

monitor = OddsMonitor()
history = monitor.load_history()

latest = history[-1]

dis = monitor.detect_disagreement(latest)

if not dis:
    print("No bookmaker disagreements detected.")
else:
    print("Detected bookmaker disagreement:\n")
    for d in dis:
        print(f"{d['match']} | {d['team']} | {d['bookmaker']} | Price: {d['price']} | Avg: {d['average']:.2f} | Δ {d['deviation']:+.2f}")
