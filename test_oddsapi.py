import requests

API_KEY = "5e2e8dc7af2c06f6b6504b0155577bb6"
SPORT = "soccer_epl"   # English Premier League
REGION = "uk"
MARKETS = "h2h"        # head-to-head odds

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"

params = {
    "apiKey": API_KEY,
    "regions": REGION,
    "markets": MARKETS,
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print("SUCCESS! Odds Retrieved:")
    print(data)
else:
    print("Error:", response.status_code, response.text)
