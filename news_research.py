import requests


def get_market_news(symbol, api_key, limit=10):
    """
    Retrieve recent financial news and sentiment
    for a stock or cryptocurrency.
    """

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "sort": "LATEST",
        "limit": limit,
        "apikey": api_key
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()
