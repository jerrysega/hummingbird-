import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

SPORTS = [
    "soccer_epl",
    "soccer_uefa_champs_league",
    "soccer_france_ligue1",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
]

def fetch_all_leagues():
    all_data = []

    for sport in SPORTS:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            params = {"apiKey": API_KEY, "regions": "eu", "oddsFormat": "decimal"}

            r = requests.get(url, params=params)

            if r.status_code != 200:
                continue

            for match in r.json():
                title = match.get("home_team") + " vs " + match.get("away_team")
                bookmakers = match.get("bookmakers", [])

                odds_dict = {}
                for b in bookmakers:
                    if b["markets"]:
                        odds_dict[b["title"]] = b["markets"][0]["outcomes"][0]["price"]

                all_data.append({
                    "title": title,
                    "market": "1X2",
                    "bookmakers_odds": odds_dict
                })

        except Exception as e:
            continue

    return all_data
