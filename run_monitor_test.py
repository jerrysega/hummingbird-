from data.odds_monitor import OddsMonitor

monitor = OddsMonitor()
changes = monitor.compare_last_two()

if not changes:
    print("No major changes detected.")
else:
    print("\nDetected line movements:\n")
    for c in changes:
        print(f"{c['match']} | {c['team']} | {c['bookmaker']} | {c['old']} → {c['new']} (Δ {c['change']})")
