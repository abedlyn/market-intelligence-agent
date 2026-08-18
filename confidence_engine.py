def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(value, maximum))


def calculate_confidence(
    evidence_scores,
    probabilities,
    adversarial_text="",
    market_context="",
    news_context="",
    sentiment_context="",
    macro_context=""
):
    """
    Estimate confidence in the quality and consistency
    of the available evidence.

    This is NOT confidence that the market will move
    in a particular direction.

    It measures confidence in the evidence supporting
    the current analysis.
    """

    if not evidence_scores:

        return {
            "score": 0,
            "label": "Very Low",
            "reasons": [
                "No usable evidence scores were returned."
            ]
        }


    # ============================================================
    # DATA AVAILABILITY
    # ============================================================

    availability_score = 0
    availability_reasons = []


    contexts = {
        "Market data": market_context,
        "News": news_context,
        "Sentiment": sentiment_context,
        "Macro": macro_context
    }


    for name, context in contexts.items():

        text = str(context).lower()

        if not text.strip():

            continue


        failure_terms = [
            "failed",
            "unavailable",
            "not available",
            "not connected",
            "do not invent",
            "no supported",
            "error:"
        ]


        has_failure = any(
            term in text
            for term in failure_terms
        )


        if not has_failure:

            availability_score += 10

        else:

            availability_reasons.append(
                f"{name} contains unavailable or "
                f"failed data."
            )


    availability_score = clamp(
        availability_score,
        0,
        40
    )


    # ============================================================
    # EVIDENCE STRENGTH
    # ============================================================

    bullish_values = []
    bearish_values = []


    for key, value in evidence_scores.items():

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue


        if "bullish" in key:

            bullish_values.append(
                numeric_value
            )

        elif "bearish" in key:

            bearish_values.append(
                numeric_value
            )


    average_bullish = (
        sum(bullish_values)
        / len(bullish_values)
        if bullish_values
        else 0
    )


    average_bearish = (
        sum(bearish_values)
        / len(bearish_values)
        if bearish_values
        else 0
    )


    average_directional_evidence = (
        average_bullish +
        average_bearish
    ) / 2


    evidence_strength_score = (
        average_directional_evidence
        * 3
    )


    evidence_strength_score = clamp(
        evidence_strength_score,
        0,
        30
    )


    # ============================================================
    # CONFLICT SCORE
    # ============================================================

    conflict_score = 20


    if probabilities:

        bullish = float(
            probabilities.get(
                "Bullish",
                0
            )
        )

        bearish = float(
            probabilities.get(
                "Bearish",
                0
            )
        )


        directional_gap = abs(
            bullish -
            bearish
        )


        if directional_gap <= 5:

            conflict_score = 5

        elif directional_gap <= 10:

            conflict_score = 8

        elif directional_gap <= 20:

            conflict_score = 12

        elif directional_gap <= 35:

            conflict_score = 16

        else:

            conflict_score = 20


    # ============================================================
    # ADVERSARIAL PENALTY
    # ============================================================

    adversarial_penalty = 0


    if adversarial_text:

        text = adversarial_text.lower()


        uncertainty_terms = [
            "uncertain",
            "uncertainty",
            "contradictory",
            "conflicting",
            "missing information",
            "weakness",
            "invalid",
            "cannot determine",
            "limited evidence"
        ]


        uncertainty_count = sum(
            text.count(term)
            for term in uncertainty_terms
        )


        adversarial_penalty = min(
            15,
            uncertainty_count * 1.5
        )


    # ============================================================
    # FINAL CONFIDENCE
    # ============================================================

    raw_score = (
        availability_score
        + evidence_strength_score
        + conflict_score
        - adversarial_penalty
    )


    confidence_score = clamp(
        raw_score,
        0,
        100
    )


    # ============================================================
    # CONFIDENCE LABEL
    # ============================================================

    if confidence_score >= 80:

        label = "Very High"

    elif confidence_score >= 65:

        label = "High"

    elif confidence_score >= 50:

        label = "Moderate"

    elif confidence_score >= 35:

        label = "Low"

    else:

        label = "Very Low"


    # ============================================================
    # REASONS
    # ============================================================

    reasons = []


    if availability_score >= 30:

        reasons.append(
            "Most external research sources "
            "were available."
        )

    elif availability_score >= 15:

        reasons.append(
            "Some external research sources "
            "were available, but gaps remain."
        )

    else:

        reasons.append(
            "Several external evidence sources "
            "were unavailable."
        )


    if average_directional_evidence >= 7:

        reasons.append(
            "Directional evidence is relatively strong."
        )

    elif average_directional_evidence >= 4:

        reasons.append(
            "Directional evidence is moderate."
        )

    else:

        reasons.append(
            "Directional evidence is weak."
        )


    if conflict_score <= 8:

        reasons.append(
            "Bullish and bearish evidence is "
            "closely balanced."
        )

    elif conflict_score >= 16:

        reasons.append(
            "Evidence shows relatively strong "
            "directional separation."
        )


    if adversarial_penalty > 0:

        reasons.append(
            "The adversarial analysis identified "
            "uncertainties or weaknesses."
        )


    reasons.extend(
        availability_reasons
    )


    return {
        "score": round(
            confidence_score,
            1
        ),

        "label": label,

        "reasons": reasons
    }


def format_confidence_report(confidence):
    """
    Format the confidence result for display.
    """

    if not confidence:

        return "Confidence could not be calculated."


    score = confidence.get(
        "score",
        0
    )

    label = confidence.get(
        "label",
        "Unknown"
    )

    reasons = confidence.get(
        "reasons",
        []
    )


    lines = [
        f"Evidence confidence: "
        f"{score}/100",

        f"Confidence level: "
        f"{label}",

        "",

        "Why:"
    ]


    for reason in reasons:

        lines.append(
            f"- {reason}"
        )


    lines.extend([
        "",
        "IMPORTANT:",
        "",
        "This confidence score measures the "
        "quality and consistency of the available "
        "evidence.",
        "",
        "It does NOT mean there is an equivalent "
        "probability that the market will move "
        "in the expected direction."
    ])


    return "\n".join(lines)
