def normalize_crypto_id(asset_name):
    """
    Convert common crypto symbols/names into CoinGecko IDs.
    """

    mapping = {
        "BTC": "bitcoin",
        "BITCOIN": "bitcoin",
        "ETH": "ethereum",
        "ETHEREUM": "ethereum",
        "SOL": "solana",
        "SOLANA": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "DOGECOIN": "dogecoin",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "MATIC": "matic-network"
    }

    cleaned = asset_name.upper().strip()

    return mapping.get(cleaned)


def build_research_prompt(asset): 
    """
    Creates the research instructions for the AI.
    """

    prompt = f"""
You are the research engine for a market-intelligence system.

Asset under investigation:
{asset}

Your job is NOT to predict the future.

Your job is to investigate the available evidence and construct
multiple plausible market scenarios.

Analyze the following categories:

1. TECHNICAL STRUCTURE
- Trend
- Market structure
- Support and resistance
- Momentum
- Volume
- Volatility
- Breakouts and breakdowns
- Relevant chart patterns

2. MARKET BEHAVIOR
- Momentum behavior
- Risk-on/risk-off behavior
- Crowd psychology
- Fear and greed
- Possible positioning
- Possible liquidity behavior

3. FUNDAMENTAL FACTORS
- Important developments affecting the asset
- Sector conditions
- Company/project fundamentals where relevant

4. MACRO ENVIRONMENT
- Interest rates
- Inflation
- Currency conditions
- Economic growth
- Major scheduled economic events
- Geopolitical factors where relevant

5. SENTIMENT
- Bullish narratives
- Bearish narratives
- Areas where sentiment appears crowded
- Conflicting signals

6. CATALYSTS
Identify events or developments that could materially change
the current situation.

7. RISKS
Identify factors that could invalidate the current thesis.

Then construct three primary scenarios:

BULLISH SCENARIO
Explain the evidence supporting it.

BEARISH SCENARIO
Explain the evidence supporting it.

NEUTRAL / RANGE SCENARIO
Explain the evidence supporting it.

For each scenario provide:

- Estimated probability
- Supporting evidence
- Contradicting evidence
- Possible catalysts
- Main risks
- Conditions that would invalidate the scenario

IMPORTANT:

These probabilities are NOT predictions.

They are analytical estimates representing how strongly the
available evidence supports each scenario.

The probabilities must add up to approximately 100%.

Never claim certainty.

Clearly distinguish:
FACT
INFERENCE
ASSUMPTION
UNCERTAINTY
"""

    return prompt
