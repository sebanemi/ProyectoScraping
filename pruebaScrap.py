import requests
import pandas as pd

API_KEY = "62149b43b7954bc8a3109a9eff9f01f4"
symbol = "AAPL"

def get_all_data(symbol):
    base_url = "https://api.twelvedata.com"

    # Quote
    quote = requests.get(f"{base_url}/quote?symbol={symbol}&apikey={API_KEY}").json()

    # Time series → DataFrame
    ts = requests.get(f"{base_url}/time_series?symbol={symbol}&interval=1day&apikey={API_KEY}").json()
    df = pd.DataFrame(ts.get("values", []))

    # Press releases
    news = requests.get(f"{base_url}/press_releases?symbol={symbol}&apikey={API_KEY}").json()

    # Earnings
    earnings = requests.get(f"{base_url}/earnings?symbol={symbol}&apikey={API_KEY}").json()

    return {
        "quote": quote,
        "history": df,
        "news": news.get("press_releases", []),
        "earnings": earnings
    }

data = get_all_data("AAPL")



