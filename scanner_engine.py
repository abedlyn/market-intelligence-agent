import time
from market_data import get_market_data


# Initial crypto market universe.
# We will expand this later as the live scanner becomes more advanced.
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
    a simple preliminary momentum score.

    This is only a screening score.
    It is NOT a prediction.
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


def scan_asset(asset_symbol):
    """
    Retrieve current market data for one asset
    and convert it into a preliminary scanner candidate.
    """

    try:
        data = get_market_data(asset_symbol)

    except Exception as error:
        return {
            "asset": asset_symbol,
            "status": "ERROR",
            "error": str(error),
        }

    if not data:
        return {
            "asset": asset_symbol,
            "status": "NO_DATA",
            "error": "No market data returned.",
        }

    price = safe_float(
        data.get("price")
    )

    change_24h = safe_float(
        data.get("change_24h")
    )

    volume = safe_float(
        data.get("volume")
    )

    market_cap = safe_float(
        data.get("market_cap")
    )

    momentum_score = calculate_market_momentum(
        change_24h
    )

    momentum_classification = classify_momentum(
        change_24h
    )

    if change_24h > 0:
        preliminary_direction = "LONG"

    elif change_24h < 0:
        preliminary_direction = "SHORT"

    else:
        preliminary_direction = "NEUTRAL"

    return {
        "asset": asset_symbol,
        "status": "OK",
        "price": price,
        "change_24h": change_24h,
        "volume": volume,
        "market_cap": market_cap,
        "momentum_score": momentum_score,
        "momentum": momentum_classification,
        "preliminary_direction": preliminary_direction,
    }


def scan_market(
    assets=None,
    delay_seconds=0.25
):
    """
    Scan a list of assets.

    Returns candidates sorted by preliminary
    market opportunity strength.

    This function does NOT execute trades.
    """

    if assets is None:
        assets = DEFAULT_ASSETS

    results = []

    for asset in assets:

        result = scan_asset(asset)

        if result.get("status") == "OK":
            results.append(result)

        if delay_seconds > 0:
            time.sleep(delay_seconds)

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

    These are screening candidates only.
    They still require full intelligence analysis.
    """

    results = scan_market(
        assets=assets
    )

    return results[:limit]


def build_scanner_summary(
    candidates
):
    """
    Create a human-readable summary of the
    current scanner results.
    """

    if not candidates:
        return "No market candidates were found."

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

        price = candidate.get(
            "price",
            0
        )

        change = candidate.get(
            "change_24h",
            0
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
            f"Price: {price} | "
            f"24h: {change:.2f}% | "
            f"{momentum} | "
            f"Bias: {direction}"
        )

    lines.append("")
    lines.append(
        "These candidates require full "
        "market-intelligence analysis before "
        "being considered opportunities."
    )

    return "\n".join(lines)


def filter_candidates(
    candidates,
    minimum_momentum_score=60
):
    """
    Filter the preliminary scanner results.

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
            filtered.append(candidate)

    return filtered


def prepare_for_intelligence_engine(
    candidates
):
    """
    Convert scanner candidates into a clean structure
    for the deeper market-intelligence pipeline.

    No trade is executed here.
    """

    prepared = []

    for candidate in candidates:

        prepared.append(
            {
                "asset": candidate.get(
                    "asset"
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
                "preliminary_direction":
                    candidate.get(
                        "preliminary_direction"
                    ),
                "requires_deep_analysis": True,
                "trade_execution": False,
            }
        )

    return prepared
