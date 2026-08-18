def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def calculate_scenario_probabilities(
    evidence_scores,
    adversarial_text=""
):
    """
    Calculate Bullish / Neutral / Bearish probabilities
    using evidence strength and adversarial analysis.

    Neutral receives additional weight when bullish
    and bearish evidence are closely balanced.
    """

    if not evidence_scores:
        return {
            "Bullish": 33.3,
            "Neutral": 33.4,
            "Bearish": 33.3
        }


    # ============================================================
    # EVIDENCE COMPONENTS
    # ============================================================

    technical_bullish = float(
        evidence_scores.get(
            "technical_bullish",
            0
        )
    )

    technical_bearish = float(
        evidence_scores.get(
            "technical_bearish",
            0
        )
    )


    momentum_bullish = float(
        evidence_scores.get(
            "momentum_bullish",
            0
        )
    )

    momentum_bearish = float(
        evidence_scores.get(
            "momentum_bearish",
            0
        )
    )


    sentiment_bullish = float(
        evidence_scores.get(
            "sentiment_bullish",
            0
        )
    )

    sentiment_bearish = float(
        evidence_scores.get(
            "sentiment_bearish",
            0
        )
    )


    fundamental_bullish = float(
        evidence_scores.get(
            "fundamental_bullish",
            0
        )
    )

    fundamental_bearish = float(
        evidence_scores.get(
            "fundamental_bearish",
            0
        )
    )


    macro_bullish = float(
        evidence_scores.get(
            "macro_bullish",
            0
        )
    )

    macro_bearish = float(
        evidence_scores.get(
            "macro_bearish",
            0
        )
    )


    # ============================================================
    # WEIGHT DIFFERENT EVIDENCE TYPES
    # ============================================================

    bullish_score = (
        technical_bullish * 1.40
        + momentum_bullish * 1.20
        + sentiment_bullish * 0.80
        + fundamental_bullish * 1.00
        + macro_bullish * 0.80
    )


    bearish_score = (
        technical_bearish * 1.40
        + momentum_bearish * 1.20
        + sentiment_bearish * 0.80
        + fundamental_bearish * 1.00
        + macro_bearish * 0.80
    )


    # ============================================================
    # BULL / BEAR BALANCE
    # ============================================================

    total_directional = (
        bullish_score +
        bearish_score
    )


    if total_directional <= 0:

        return {
            "Bullish": 33.3,
            "Neutral": 33.4,
            "Bearish": 33.3
        }


    difference = abs(
        bullish_score -
        bearish_score
    )


    balance_ratio = (
        difference /
        total_directional
    )


    # ============================================================
    # BASE DIRECTIONAL PROBABILITIES
    # ============================================================

    bullish_share = (
        bullish_score /
        total_directional
    )

    bearish_share = (
        bearish_score /
        total_directional
    )


    # ============================================================
    # NEUTRAL WEIGHT
    # ============================================================

    # Closely balanced evidence gets a much larger
    # neutral allocation.

    if balance_ratio <= 0.05:

        neutral_weight = 0.50

    elif balance_ratio <= 0.10:

        neutral_weight = 0.40

    elif balance_ratio <= 0.20:

        neutral_weight = 0.30

    elif balance_ratio <= 0.30:

        neutral_weight = 0.20

    elif balance_ratio <= 0.40:

        neutral_weight = 0.12

    else:

        neutral_weight = 0.07


    # ============================================================
    # DIRECTIONAL ALLOCATION
    # ============================================================

    remaining = (
        1.0 -
        neutral_weight
    )


    bullish_probability = (
        bullish_share *
        remaining
    )


    bearish_probability = (
        bearish_share *
        remaining
    )


    # ============================================================
    # ADVERSARIAL ADJUSTMENT
    # ============================================================

    # The adversarial engine is deliberately used
    # as a modest adjustment rather than allowing
    # text alone to dominate the probabilities.

    if adversarial_text:

        text = adversarial_text.lower()


        bullish_weakness_terms = [
            "bull case weaknesses",
            "bull case weakness",
            "bullish case is weak",
            "bullish case depends",
            "bullish thesis is weak"
        ]


        bearish_weakness_terms = [
            "bear case weaknesses",
            "bear case weakness",
            "bearish case is weak",
            "bearish case depends",
            "bearish thesis is weak"
        ]


        bullish_weakness = sum(
            term in text
            for term in bullish_weakness_terms
        )


        bearish_weakness = sum(
            term in text
            for term in bearish_weakness_terms
        )


        if bullish_weakness > bearish_weakness:

            adjustment = min(
                0.05,
                bullish_weakness * 0.02
            )

            bullish_probability -= adjustment
            bearish_probability += adjustment


        elif bearish_weakness > bullish_weakness:

            adjustment = min(
                0.05,
                bearish_weakness * 0.02
            )

            bearish_probability -= adjustment
            bullish_probability += adjustment


    # ============================================================
    # NORMALIZE
    # ============================================================

    bullish_probability = clamp(
        bullish_probability,
        0.0,
        1.0
    )

    bearish_probability = clamp(
        bearish_probability,
        0.0,
        1.0
    )


    neutral_probability = max(
        0.0,
        1.0
        - bullish_probability
        - bearish_probability
    )


    total = (
        bullish_probability +
        neutral_probability +
        bearish_probability
    )


    bullish_probability /= total
    neutral_probability /= total
    bearish_probability /= total


    # ============================================================
    # RETURN PERCENTAGES
    # ============================================================

    return {
        "Bullish": round(
            bullish_probability * 100,
            1
        ),

        "Neutral": round(
            neutral_probability * 100,
            1
        ),

        "Bearish": round(
            bearish_probability * 100,
            1
        )
      }
