import requests


def get_market_data(symbol):
    """
    Get basic current market data for a crypto asset
    from CoinGecko's public API.
    """

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": symbol.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
        "include_market_cap": "true"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()
