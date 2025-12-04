import requests


class OddsFetcher:
    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_odds(self, sport, regions="uk,eu", markets="h2h,spreads,totals"):
        """Fetches odds for a given sport from OddsAPI."""

        url = f"{self.BASE_URL}/sports/{sport}/odds/"

        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": markets,
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print("\n❌ Error fetching odds:")
            print("Status:", response.status_code)
            print("Message:", response.text)
            return None
