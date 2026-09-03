import time

from market_data import get_market_data
from research_engine import normalize_crypto_id


DEFAULT_ASSETS = [
    "BTC",
    "ETH",
    "BNB",
    "SOL",
    "XRP",
    "ADA",
    "DOGE",
    "AVAX",
    "LINK",
    "DOT",
]


def safe_float(value, default=0.0):
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_market_momentum(change_24h):
    """
    Convert 24-hour percentage movement into
    a preliminary momentum score.

    This is a screening score, not a prediction.
    """

    change_24h = safe_float(change_24h)

    if change_24h >= 10:
        return 100

    if change_24h >= 5:
        return 85

    if change_24h >= 3:
        return 75

    if change_24h >= 1:
        return 65

    if change_24h >= 0:
        return 55

    if change_24h >= -1:
        return 45

    if change_24h >= -3:
        return 35

    if change_24h >= -5:
        return 25

    if change_24h >= -10:
        return 15

    return 5


def classify_momentum(change_24h):
    """Classify short-term market momentum."""

    change_24h = safe_float(change_24h)

    if change_24h >= 3:
        return "BULLISH MOMENTUM"

    if change_24h <= -3:
        return "BEARISH MOMENTUM"

    return "NEUTRAL MOMENTUM"


def extract_coin_data(raw_data, crypto_id):
    """
    Extract the actual CoinGecko asset object.

    market_data.py returns data in this structure:

        {
            "bitcoin": {
                "usd": ...,
                "usd_24h_change": ...,
                "usd_24h_vol": ...,
                "usd_market_cap": ...
            }
        }
    """

    if not isinstance(raw_data, dict):
        return {}

    coin_data = raw_data.get(crypto_id)

    if isinstance(coin_data, dict):
        return coin_data

    return {}


def scan_asset(asset_symbol):
    """
    Retrieve current market data for one supported crypto asset
    and convert it into a preliminary scanner candidate.
    """

    asset_symbol = (
        str(asset_symbol)
        .strip()
        .upper()
    )

    crypto_id = normalize_crypto_id(
        asset_symbol
    )

    if not crypto_id:
        return {
            "asset": asset_symbol,
            "status": "UNSUPPORTED",
            "error": (
                "Asset is not currently supported "
                "by the crypto market-data mapping."
            ),
        }

    try:
        raw_data = get_market_data(
            crypto_id
        )

    except Exception as error:
        return {
            "asset": asset_symbol,
            "crypto_id": crypto_id,
            "status": "ERROR",
            "error": str(error),
        }

    coin_data = extract_coin_data(
        raw_data,
        crypto_id
    )

    if not coin_data:
        return {
            "asset": asset_symbol,
            "crypto_id": crypto_id,
            "status": "NO_DATA",
            "error": (
                "No market data was returned "
                "for this asset."
            ),
        }

    price = safe_float(
        coin_data.get("usd")
    )

    change_24h = safe_float(
        coin_data.get("usd_24h_change")
    )

    volume = safe_float(
        coin_data.get("usd_24h_vol")
    )

    market_cap = safe_float(
        coin_data.get("usd_market_cap")
    )

    momentum_score = (
        calculate_market_momentum(
            change_24h
        )
    )

    momentum_classification = (
        classify_momentum(
            change_24h
        )
    )

    if change_24h > 0:
        preliminary_direction = "LONG"

    elif change_24h < 0:
        preliminary_direction = "SHORT"

    else:
        preliminary_direction = "NEUTRAL"

    return {
        "asset": asset_symbol,
        "crypto_id": crypto_id,
        "status": "OK",
        "price": price,
        "change_24h": change_24h,
        "volume": volume,
        "market_cap": market_cap,
        "momentum_score": momentum_score,
        "momentum": momentum_classification,
        "preliminary_direction": (
            preliminary_direction
        ),
    }


def scan_market(
    assets=None,
    delay_seconds=0.25
):
    """
    Scan a list of crypto assets.

    Results are sorted by preliminary momentum strength.

    No trade is executed.
    """

    if assets is None:
        assets = DEFAULT_ASSETS

    results = []

    for asset in assets:

        result = scan_asset(
            asset
        )

        if result.get(
            "status"
        ) == "OK":

            results.append(
                result
            )

        if delay_seconds > 0:
            time.sleep(
                delay_seconds
            )

    results.sort(
        key=lambda item: (
            item.get(
                "momentum_score",
                0
            )
        ),
        reverse=True
    )

    return results


def get_top_candidates(
    assets=None,
    limit=5
):
    """
    Return the strongest preliminary candidates.

    These candidates still require full
    market-intelligence analysis.
    """

    results = scan_market(
        assets=assets
    )

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 5

    if limit < 1:
        limit = 1

    return results[:limit]


def filter_candidates(
    candidates,
    minimum_momentum_score=60
):
    """
    Filter preliminary candidates.

    Only candidates with meaningful momentum
    are passed to the deeper intelligence layer.
    """

    filtered = []

    for candidate in candidates:

        if candidate.get(
            "status"
        ) != "OK":
            continue

        score = safe_float(
            candidate.get(
                "momentum_score",
                0
            )
        )

        if score >= minimum_momentum_score:
            filtered.append(
                candidate
            )

    return filtered


def rank_candidates(
    candidates
):
    """
    Rank scanner candidates.

    Higher preliminary momentum scores appear first.
    """

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.get(
                "momentum_score",
                0
            ),
            abs(
                safe_float(
                    candidate.get(
                        "change_24h",
                        0
                    )
                )
            )
        ),
        reverse=True
    )


def prepare_for_intelligence_engine(
    candidates
):
    """
    Convert scanner candidates into a clean structure
    for the deeper intelligence pipeline.

    No trade execution occurs here.
    """

    prepared = []

    for candidate in candidates:

        prepared.append(
            {
                "asset": candidate.get(
                    "asset"
                ),
                "crypto_id": candidate.get(
                    "crypto_id"
                ),
                "price": candidate.get(
                    "price"
                ),
                "change_24h": candidate.get(
                    "change_24h"
                ),
                "volume": candidate.get(
                    "volume"
                ),
                "market_cap": candidate.get(
                    "market_cap"
                ),
                "momentum_score": candidate.get(
                    "momentum_score"
                ),
                "momentum": candidate.get(
                    "momentum"
                ),
                "preliminary_direction":
                    candidate.get(
                        "preliminary_direction"
                    ),
                "requires_deep_analysis": True,
                "trade_execution": False,
            }
        )

    return prepared


def build_scanner_summary(
    candidates
):
    """
    Create a readable summary of scanner results.
    """

    if not candidates:
        return (
            "No market candidates were found."
        )

    lines = [
        "LIVE MARKET SCANNER",
        "",
        "Preliminary candidates:",
        ""
    ]

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        asset = candidate.get(
            "asset",
            "UNKNOWN"
        )

        price = safe_float(
            candidate.get(
                "price",
                0
            )
        )

        change = safe_float(
            candidate.get(
                "change_24h",
                0
            )
        )

        momentum = candidate.get(
            "momentum",
            "UNKNOWN"
        )

        direction = candidate.get(
            "preliminary_direction",
            "NEUTRAL"
        )

        lines.append(
            f"{index}. {asset} | "
            f"Price: ${price:,.6f} | "
            f"24h: {change:+.2f}% | "
            f"{momentum} | "
            f"Bias: {direction}"
        )

    lines.append("")

    lines.append(
        "These are screening candidates only. "
        "They require full market-intelligence "
        "analysis before becoming opportunities."
    )

    return "\n".join(
        lines
        )
