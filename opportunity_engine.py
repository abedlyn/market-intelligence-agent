def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def calculate_opportunity_score(
    scenario_probabilities,
    confidence_score,
    risk_reward=0,
    catalyst_score=0,
    timeframe_alignment=0
):
    """
    Calculate a setup-quality score.

    This is NOT a probability of winning a trade.

    It measures how attractive and well-supported
    a potential market setup appears based on the
    available evidence.
    """

    bullish = float(
        scenario_probabilities.get("Bullish", 0)
    )

    bearish = float(
        scenario_probabilities.get("Bearish", 0)
    )

    neutral = float(
        scenario_probabilities.get("Neutral", 0)
    )


    # ============================================================
    # DIRECTIONAL STRENGTH
    # ============================================================

    directional_strength = max(
        bullish,
        bearish
    )


    # ============================================================
    # DIRECTIONAL CLARITY
    # ============================================================

    directional_gap = abs(
        bullish - bearish
    )


    clarity_score = clamp(
        directional_gap * 2
    )


    # ============================================================
    # RISK / REWARD
    # ============================================================

    if risk_reward > 0:

        risk_reward_score = clamp(
            risk_reward * 20
        )

    else:

        risk_reward_score = 0


    # ============================================================
    # TIMEFRAME ALIGNMENT
    # ============================================================

    timeframe_score = clamp(
        timeframe_alignment
    )


    # ============================================================
    # CATALYST
    # ============================================================

    catalyst_score = clamp(
        catalyst_score
    )


    # ============================================================
    # CONFIDENCE
    # ============================================================

    confidence_score = clamp(
        confidence_score
    )


    # ============================================================
    # NEUTRAL PENALTY
    # ============================================================

    # High Neutral probability means the market direction
    # is less clearly established.

    neutral_penalty = (
        neutral * 0.25
    )


    # ============================================================
    # FINAL SETUP SCORE
    # ============================================================

    score = (
        directional_strength * 0.30
        +
        clarity_score * 0.20
        +
        confidence_score * 0.20
        +
        risk_reward_score * 0.10
        +
        timeframe_score * 0.10
        +
        catalyst_score * 0.10
        -
        neutral_penalty
    )


    return round(
        clamp(score)
    )


def determine_direction(
    scenario_probabilities
):
    """
    Determine the dominant proposed direction.

    Returns:
        LONG
        SHORT
        NEUTRAL
    """

    bullish = float(
        scenario_probabilities.get(
            "Bullish",
            0
        )
    )

    bearish = float(
        scenario_probabilities.get(
            "Bearish",
            0
        )
    )

    neutral = float(
        scenario_probabilities.get(
            "Neutral",
            0
        )
    )


    if (
        neutral >= bullish
        and
        neutral >= bearish
    ):

        return "NEUTRAL"


    if bullish > bearish:

        return "LONG"


    if bearish > bullish:

        return "SHORT"


    return "NEUTRAL"


def classify_opportunity(
    score,
    direction
):
    """
    Convert the setup score into a readable category.
    """

    if direction == "NEUTRAL":

        return "NO CLEAR TRADE"


    if score >= 85:

        return "A+ SETUP"


    if score >= 75:

        return "STRONG SETUP"


    if score >= 65:

        return "PROMISING SETUP"


    if score >= 50:

        return "WATCHLIST"


    return "WEAK SETUP"


def build_opportunity(
    asset_symbol,
    scenario_probabilities,
    confidence_score,
    risk_reward=0,
    catalyst_score=0,
    timeframe_alignment=0,
    entry_zone=None,
    stop_loss=None,
    targets=None,
    reason=""
):
    """
    Build a standardized market opportunity object.
    """

    direction = determine_direction(
        scenario_probabilities
    )


    score = calculate_opportunity_score(
        scenario_probabilities=
            scenario_probabilities,
        confidence_score=
            confidence_score,
        risk_reward=
            risk_reward,
        catalyst_score=
            catalyst_score,
        timeframe_alignment=
            timeframe_alignment
    )


    classification = classify_opportunity(
        score,
        direction
    )


    return {
        "asset": asset_symbol,

        "direction": direction,

        "setup_score": score,

        "classification": classification,

        "scenario_probabilities":
            scenario_probabilities,

        "confidence": confidence_score,

        "risk_reward": risk_reward,

        "catalyst_score": catalyst_score,

        "timeframe_alignment":
            timeframe_alignment,

        "entry_zone": entry_zone,

        "stop_loss": stop_loss,

        "targets": targets or [],

        "reason": reason,

        "requires_approval": True,

        "status": "PENDING_APPROVAL"
    }


def rank_opportunities(
    opportunities
):
    """
    Rank opportunities from strongest to weakest.

    Neutral/no-trade setups are pushed below
    actionable directional setups.
    """

    ranked = sorted(
        opportunities,
        key=lambda opportunity: (
            opportunity.get(
                "direction"
            ) != "NEUTRAL",
            opportunity.get(
                "setup_score",
                0
            )
        ),
        reverse=True
    )


    return ranked


def format_opportunity(
    opportunity
):
    """
    Create a concise human-readable opportunity summary.
    """

    asset = opportunity.get(
        "asset",
        "UNKNOWN"
    )

    direction = opportunity.get(
        "direction",
        "NEUTRAL"
    )

    score = opportunity.get(
        "setup_score",
        0
    )

    classification = opportunity.get(
        "classification",
        "UNKNOWN"
    )

    confidence = opportunity.get(
        "confidence",
        0
    )

    probabilities = opportunity.get(
        "scenario_probabilities",
        {}
    )

    bullish = probabilities.get(
        "Bullish",
        0
    )

    neutral = probabilities.get(
        "Neutral",
        0
    )

    bearish = probabilities.get(
        "Bearish",
        0
    )


    return f"""
### {asset}

**Direction:** {direction}

**Setup Quality:** {score}/100

**Classification:** {classification}

**Evidence Confidence:** {confidence}/100

**Scenario Balance:**

🐂 Bullish: {bullish}%

⚖️ Neutral: {neutral}%

🐻 Bearish: {bearish}%

**Why it is interesting:**

{opportunity.get("reason", "No explanation available.")}

**Approval Required:** YES

**Status:** PENDING APPROVAL
"""


def get_actionable_opportunities(
    opportunities,
    minimum_score=65
):
    """
    Return only opportunities that are strong enough
    to deserve attention.

    This does NOT execute trades.
    """

    ranked = rank_opportunities(
        opportunities
    )


    actionable = []

    for opportunity in ranked:

        if (
            opportunity.get(
                "direction"
            ) != "NEUTRAL"
            and
            opportunity.get(
                "setup_score",
                0
            ) >= minimum_score
        ):

            actionable.append(
                opportunity
            )


    return actionable
