from odds_engine import OddsFetcher

api = OddsFetcher("5e2e8dc7af2c06f6b6504b0155577bb6")

data = api.get_odds("soccer_epl")

print(data[:1])   # show only first match to avoid too much text
