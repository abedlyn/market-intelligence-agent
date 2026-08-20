import re


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def extract_adversarial_scores(adversarial_text):
    """
    Extract optional numeric Bull/Bear strength scores
    from the adversarial analysis.

    If scores are unavailable, return neutral defaults.
    """

    text = adversarial_text.lower()

    bullish_score = None
    bearish_score = None

    bullish_patterns = [
        r"bull(?:ish)?[^0-9]{0,30}(\d{1,3})\s*(?:/10|%)?",
        r"bull case[^0-9]{0,30}(\d{1,3})",
        r"bull strength[^0-9]{0,30}(\d{1,3})"
    ]

    bearish_patterns = [
        r"bear(?:ish)?[^0-9]{0,30}(\d{1,3})\s*(?:/10|%)?",
        r"bear case[^0-9]{0,30}(\d{1,3})",
        r"bear strength[^0-9]{0,30}(\d{1,3})"
    ]

    for pattern in bullish_patterns:

        match = re.search(pattern, text)

        if match:
            bullish_score = float(match.group(1))
            break

    for pattern in bearish_patterns:

        match = re.search(pattern, text)

        if match:
            bearish_score = float(match.group(1))
            break

    if bullish_score is None:
        bullish_score = 5.0

    if bearish_score is None:
        bearish_score = 5.0

    # Convert percentages above 10 into a 0-10 scale
    if bullish_score > 10:
        bullish_score = bullish_score / 10

    if bearish_score > 10:
        bearish_score = bearish_score / 10

    return {
        "bullish": clamp(bullish_score, 0, 10),
        "bearish": clamp(bearish_score, 0, 10)
    }


def calculate_base_directional_scores(evidence_scores):
    """
    Calculate bullish and bearish evidence strength
    from the structured evidence engine.
    """

    bullish_keys = [
        "technical_bullish",
        "momentum_bullish",
        "sentiment_bullish",
        "fundamental_bullish",
        "macro_bullish"
    ]

    bearish_keys = [
        "technical_bearish",
        "momentum_bearish",
        "sentiment_bearish",
        "fundamental_bearish",
        "macro_bearish"
    ]

    bullish_values = [
        float(evidence_scores.get(key, 0))
        for key in bullish_keys
    ]

    bearish_values = [
        float(evidence_scores.get(key, 0))
        for key in bearish_keys
    ]

    bullish_total = sum(bullish_values)
    bearish_total = sum(bearish_values)

    return bullish_total, bearish_total


def calculate_scenario_probabilities(
    evidence_scores,
    adversarial_text=""
):
    """
    Evidence-weighted Bullish / Neutral / Bearish engine.

    The adversarial engine acts as a second layer of scrutiny.

    Neutral receives additional weight when bullish and
    bearish evidence are closely balanced.
    """

    bullish_total, bearish_total = (
        calculate_base_directional_scores(
            evidence_scores
        )
    )

    adversarial = extract_adversarial_scores(
        adversarial_text
    )

    adversarial_bullish = adversarial["bullish"]
    adversarial_bearish = adversarial["bearish"]


    # ============================================================
    # BASE DIRECTIONAL BALANCE
    # ============================================================

    total_directional = (
        bullish_total +
        bearish_total
    )

    if total_directional <= 0:

        base_bullish = 50.0
        base_bearish = 50.0

    else:

        base_bullish = (
            bullish_total /
            total_directional
        ) * 100

        base_bearish = (
            bearish_total /
            total_directional
        ) * 100


    # ============================================================
    # ADVERSARIAL ADJUSTMENT
    # ============================================================

    adversarial_total = (
        adversarial_bullish +
        adversarial_bearish
    )

    if adversarial_total > 0:

        adversarial_bull_pct = (
            adversarial_bullish /
            adversarial_total
        )

        adversarial_bear_pct = (
            adversarial_bearish /
            adversarial_total
        )

    else:

        adversarial_bull_pct = 0.5
        adversarial_bear_pct = 0.5


    # Blend original evidence with adversarial evidence.
    #
    # 70% = structured evidence
    # 30% = adversarial challenge

    blended_bullish = (
        (base_bullish / 100) * 0.70
        +
        adversarial_bull_pct * 0.30
    )

    blended_bearish = (
        (base_bearish / 100) * 0.70
        +
        adversarial_bear_pct * 0.30
    )


    # ============================================================
    # DIRECTIONAL BALANCE
    # ============================================================

    directional_gap = abs(
        blended_bullish -
        blended_bearish
    )


    # ============================================================
    # NEUTRAL ENGINE
    # ============================================================

    # The closer Bull and Bear are,
    # the more Neutral receives weight.

    if directional_gap <= 0.05:

        neutral_weight = 0.50

    elif directional_gap <= 0.10:

        neutral_weight = 0.40

    elif directional_gap <= 0.15:

        neutral_weight = 0.30

    elif directional_gap <= 0.25:

        neutral_weight = 0.20

    else:

        neutral_weight = 0.10


    # ============================================================
    # APPLY NEUTRAL WEIGHT
    # ============================================================

    directional_weight = (
        1.0 -
        neutral_weight
    )

    bullish_probability = (
        blended_bullish /
        (
            blended_bullish +
            blended_bearish
        )
    ) * directional_weight

    bearish_probability = (
        blended_bearish /
        (
            blended_bullish +
            blended_bearish
        )
    ) * directional_weight

    neutral_probability = neutral_weight


    # ============================================================
    # CONVERT TO PERCENTAGES
    # ============================================================

    bullish_probability *= 100
    bearish_probability *= 100
    neutral_probability *= 100


    # ============================================================
    # ROUNDING
    # ============================================================

    bullish_probability = round(
        bullish_probability
    )

    bearish_probability = round(
        bearish_probability
    )

    neutral_probability = round(
        neutral_probability
    )


    # ============================================================
    # FORCE TOTAL = 100
    # ============================================================

    total = (
        bullish_probability +
        bearish_probability +
        neutral_probability
    )

    difference = 100 - total

    if difference != 0:

        if bullish_probability >= bearish_probability:

            bullish_probability += difference

        else:

            bearish_probability += difference


    # ============================================================
    # FINAL SAFETY CLAMP
    # ============================================================

    bullish_probability = clamp(
        bullish_probability
    )

    neutral_probability = clamp(
        neutral_probability
    )

    bearish_probability = clamp(
        bearish_probability
    )


    return {
        "Bullish": bullish_probability,
        "Neutral": neutral_probability,
        "Bearish": bearish_probability
    }
