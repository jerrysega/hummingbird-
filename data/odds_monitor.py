import os
import json
import requests
from datetime import datetime
from modules.backup_manager import BackupManager


class DailyBackupManager:
    def __init__(self, daily_folder="backups/daily", history_path="data/odds_history.json"):
        self.daily_folder = daily_folder
        self.history_path = history_path
        os.makedirs(self.daily_folder, exist_ok=True)

    def archive_today(self):
        if not os.path.exists(self.history_path):
            return

        with open(self.history_path, "r") as f:
            history = json.load(f)

        if not history:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        archive_path = os.path.join(self.daily_folder, f"{today}.json")

        # Save entire history for today
        with open(archive_path, "w") as f:
            json.dump(history, f, indent=4)

        # Reset today's file
        with open(self.history_path, "w") as f:
            json.dump([], f)

        print(f"📁 Daily archive created → {archive_path}")

class OddsMonitor:
    def __init__(self, api_key, history_path="data/odds_history.json"):
        self.api_key = api_key
        self.history_path = history_path
        self.backup = BackupManager()
        self.daily_backup = DailyBackupManager()

    def fetch_current_odds(self):
        SPORTS = [
            "soccer_epl",
            "soccer_uefa_champs_league",
            "soccer_france_ligue_one",
            "soccer_spain_la_liga",
            "soccer_italy_serie_a",
            "soccer_germany_bundesliga"
        ]

        combined = []  # merged results from all leagues

        print("📡 Fetching odds from all leagues...\n")

        for sport in SPORTS:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }

            print(f"⚽ Fetching: {sport}")

            try:
                response = requests.get(url, params=params)

                if response.status_code != 200:
                    print(f"❌ Error {response.status_code} for {sport}")
                    print(response.text)
                    continue

                data = response.json()

                # Tag each match with league name
                for match in data:
                    match["league"] = sport

                combined.extend(data)

            except Exception as e:
                print(f"❌ Failed fetching {sport}:", e)
                continue

        if not combined:
            print("❌ No odds returned from ANY league.")
            return None

        print(f"\n✅ Total matches fetched: {len(combined)}")

        return {
            "timestamp": datetime.now().isoformat(),
            "data": combined
        }

    def save_history(self, history):
        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2)


    def load_history(self):
        with open(self.history_path, "r") as f:
            return json.load(f)

    def compare_last_two(self):
        history = self.load_history()

        if len(history) < 2:
            print("Not enough data to compare yet.")
            return

        prev = history[-2]
        latest = history[-1]

        print(f"\nComparing snapshots:")
        print(f"Previous: {prev['timestamp']}")
        print(f"Latest:   {latest['timestamp']}\n")

        changes = []

        # loop through games
        for game_latest in latest["data"]:
            game_id = game_latest["id"]

            # find same game in previous snapshot
            game_prev = next((g for g in prev["data"] if g["id"] == game_id), None)
            if game_prev is None:
                continue

            # loop through bookmakers & odds
            for bm_latest in game_latest["bookmakers"]:
                bm_key = bm_latest["key"]

                bm_prev = next((b for b in game_prev["bookmakers"] if b["key"] == bm_key), None)
                if bm_prev is None:
                    continue

                # h2h market
                market_latest = next((m for m in bm_latest["markets"] if m["key"] == "h2h"), None)
                market_prev = next((m for m in bm_prev["markets"] if m["key"] == "h2h"), None)

                if not market_latest or not market_prev:
                    continue

                for i in range(len(market_latest["outcomes"])):
                    team_latest = market_latest["outcomes"][i]
                    team_prev = market_prev["outcomes"][i]

                    if team_latest["price"] != team_prev["price"]:
                        diff = team_latest["price"] - team_prev["price"]

                        changes.append({
                            "match": game_latest["home_team"] + " vs " + game_latest["away_team"],
                            "team": team_latest["name"],
                            "bookmaker": bm_key,
                            "old": team_prev["price"],
                            "new": team_latest["price"],
                            "change": diff
                        })

        return changes
    def filter_sharp_changes(self, changes, threshold=0.20):
        """
        Only return changes that exceed a certain movement threshold.
        Example: threshold=0.20 means ignore changes smaller than 0.20
        """
        sharp = [c for c in changes if abs(c["change"]) >= threshold]
        return sharp
    def detect_disagreement(self, snapshot):
        """
        Detects when one bookmaker has odds that are significantly different
        from others for the same match/team.
        """
        disagreements = []

        for game in snapshot["data"]:
            match = game["home_team"] + " vs " + game["away_team"]

            # Collect all h2h prices per team per bookmaker
            prices = {}  # {team: [list of prices]}

            for bm in game["bookmakers"]:
                market = next((m for m in bm["markets"] if m["key"] == "h2h"), None)
                if not market:
                    continue

                for outcome in market["outcomes"]:
                    team = outcome["name"]
                    price = outcome["price"]

                    if team not in prices:
                        prices[team] = []
                    prices[team].append((bm["key"], price))

            # Analyze disagreement per team
            for team, bm_prices in prices.items():
                values = [p[1] for p in bm_prices]
                avg = sum(values) / len(values)

                for bookmaker, price in bm_prices:
                    deviation = price - avg

                    # Threshold for disagreement
                    if abs(deviation) >= 0.25:
                        disagreements.append({
                            "match": match,
                            "team": team,
                            "bookmaker": bookmaker,
                            "price": price,
                            "average": avg,
                            "deviation": deviation
                        })

        return disagreements

    def monitor_once(self, bot):
        # --- MIDNIGHT DAILY ARCHIVE ---
        if datetime.now().strftime("%H:%M") == "00:00":
            self.daily_backup.archive_today()
        # ------------------------------

        # 1. Fetch live odds
        snapshot = self.fetch_current_odds()


        if not snapshot:
            print("❌ No odds fetched.")
            return
            # --- BACKUP SNAPSHOT ---
        self.backup.save_backup(snapshot)

        # 2. Load old history
        history = self.load_history()

        # 3. Save new snapshot
        history.append(snapshot)
        self.save_history(history)

        print("📦 Snapshot saved. Total snapshots:", len(history))

        # If not enough snapshots, don't compare
        if len(history) < 2:
            print("ℹ️ Not enough data to compare yet.")
            return

        # 4. Get movements
        changes = self.compare_last_two()

        if changes:
            sharp = self.filter_sharp_changes(changes, threshold=0.20)

            for c in sharp:
                msg = (
                    f"Sharp Line Movement Detected\n"
                    f"📌Match: {c['match']}\n"
                    f"🏷Team: {c['team']}\n"
                    f"🏦Bookmaker: {c['bookmaker']}\n"
                    f"📉Old: {c['old']}\n"
                    f"📈New: {c['new']}\n"
                    f"⚡Change: {c['change']:+.2f}"
                )


        # 5. Detect bookmaker disagreement
        disagreements = self.detect_disagreement(snapshot)

        for d in disagreements:
            msg = (
                f"Bookmaker Disagreement Detected\n"
                f"📌Match: {d['match']}\n"
                f"🏷Team: {d['team']}\n"
                f"🏦Bookmaker: {d['bookmaker']}\n"
                f"💰Price: {d['price']}\n"
                f"📊Market Avg: {d['average']:.2f}\n"
                f"⚠️Deviation: {d['deviation']:+.2f}"
            )

            alerts = []

            # add sharp moves to alerts
            # add disagreements to alerts

            if alerts:
                combined = "📡 Hummingbird Signals\n\n" + "\n".join(alerts)
                bot.send_message(combined)




