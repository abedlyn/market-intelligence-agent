def calculate_scenario_probabilities(
    bullish_score,
    bearish_score,
    neutral_score
):
    """
    Convert evidence scores into scenario probabilities.

    Scores represent the strength of evidence, not price predictions.
    """

    bullish_score = max(0, bullish_score)
    bearish_score = max(0, bearish_score)
    neutral_score = max(0, neutral_score)

    total = (
        bullish_score
        + bearish_score
        + neutral_score
    )

    if total == 0:
        return {
            "bullish": 33.3,
            "neutral": 33.4,
            "bearish": 33.3
        }

    bullish_probability = (
        bullish_score / total
    ) * 100

    neutral_probability = (
        neutral_score / total
    ) * 100

    bearish_probability = (
        bearish_score / total
    ) * 100

    return {
        "bullish": round(bullish_probability, 1),
        "neutral": round(neutral_probability, 1),
        "bearish": round(bearish_probability, 1)
    }


def build_evidence_summary(
    technical_bullish,
    technical_bearish,
    momentum_bullish,
    momentum_bearish,
    sentiment_bullish,
    sentiment_bearish,
    fundamental_bullish,
    fundamental_bearish,
    macro_bullish,
    macro_bearish
):
    """
    Combine evidence from different research categories.
    """

    bullish_score = (
        technical_bullish
        + momentum_bullish
        + sentiment_bullish
        + fundamental_bullish
        + macro_bullish
    )

    bearish_score = (
        technical_bearish
        + momentum_bearish
        + sentiment_bearish
        + fundamental_bearish
        + macro_bearish
    )

    neutral_score = 1

    probabilities = calculate_scenario_probabilities(
        bullish_score,
        bearish_score,
        neutral_score
    )

    return {
        "bullish_score": bullish_score,
        "bearish_score": bearish_score,
        "neutral_score": neutral_score,
        "probabilities": probabilities
    }


def format_probability_report(probabilities):
    """
    Create a simple readable probability report.
    """

    return f"""
SCENARIO PROBABILITIES

🟢 Bullish: {probabilities["bullish"]}%

🟡 Neutral / Range: {probabilities["neutral"]}%

🔴 Bearish: {probabilities["bearish"]}%

These percentages represent evidence-weighted scenario
estimates. They are not predictions or guarantees.
"""
