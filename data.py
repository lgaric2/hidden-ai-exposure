import os
import pandas as pd
import yfinance as yf

# which currency each exchange trades in (no suffix = US)
CURRENCY = {".ST": "SEK", ".CO": "DKK", ".OL": "NOK", ".SW": "CHF",
            ".PA": "EUR", ".DE": "EUR", ".AS": "EUR"}


def get_currency(ticker):
    for suffix in CURRENCY:
        if ticker.endswith(suffix):
            return CURRENCY[suffix]
    return "USD"


def download(tickers, start, end):
    # auto_adjust=True -> prices adjusted for dividends and splits
    df = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    return df["Close"]


def get_prices_sek(tickers, start, end=None):
    # save to csv so I don't have to download every time
    os.makedirs("data", exist_ok=True)
    if os.path.exists("data/prices.csv"):
        prices = pd.read_csv("data/prices.csv", index_col=0, parse_dates=True)
        fx = pd.read_csv("data/fx.csv", index_col=0, parse_dates=True)
    else:
        prices = download(tickers, start, end)
        currencies = set(get_currency(t) for t in tickers) - {"SEK"}
        fx = download([c + "SEK=X" for c in currencies], start, end)
        fx.columns = [c.replace("SEK=X", "") for c in fx.columns]
        prices.to_csv("data/prices.csv")
        fx.to_csv("data/fx.csv")

    # convert everything to SEK using that day's exchange rate
    fx = fx.reindex(prices.index).ffill()
    prices_sek = prices.copy()
    for t in tickers:
        ccy = get_currency(t)
        if ccy != "SEK":
            prices_sek[t] = prices[t] * fx[ccy]
    return prices_sek[tickers]


def weekly_returns(prices):
    # friday to friday. ffill so a holiday friday still gets a price
    weekly = prices.ffill(limit=3).resample("W-FRI").last()
    return weekly.pct_change(fill_method=None).iloc[1:]
