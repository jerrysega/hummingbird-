import json
import os
from datetime import datetime
from odds_engine import OddsFetcher


class OddsTracker:
    def __init__(self, api_key):
        self.fetcher = OddsFetcher(api_key)
        self.storage_path = "data/odds_history.json"

        # Create file if not exists
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump([], f)

    def save_snapshot(self, sport="soccer_epl"):
        """Fetch odds and save them with timestamp."""
        data = self.fetcher.get_odds(sport)

        if data is None:
            print("❌ No data to save.")
            return

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "sport": sport,
            "data": data
        }

        # Load existing history
        with open(self.storage_path, "r") as f:
            history = json.load(f)

        history.append(snapshot)

        # Save with indent for readability
        with open(self.storage_path, "w") as f:
            json.dump(history, f, indent=2)

        print(f"📦 Snapshot saved ({sport}) @ {snapshot['timestamp']}")
