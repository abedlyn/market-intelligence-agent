import time
import streamlit as st
from google import genai
from google.genai import types

from research_engine import (
    build_research_prompt,
    normalize_crypto_id
)

from market_data import get_market_data
from news_research import get_market_news

from news_processor import (
    process_news_data,
    format_news_for_ai
)

from macro_research import (
    get_macro_data,
    format_macro_for_ai
)

from sentiment_research import (
    calculate_news_sentiment,
    format_sentiment_for_ai
)

from adversarial_engine import (
    build_adversarial_prompt
)

from evidence_engine import (
    extract_evidence_scores
)

from scenario_engine import (
    calculate_scenario_probabilities
)

from confidence_engine import (
    calculate_confidence,
    format_confidence_report
)

from timeframe_engine import (
    build_timeframe_prompt
)

from catalyst_engine import (
    build_catalyst_prompt
)

from opportunity_engine import (
    build_opportunity,
    get_actionable_opportunities,
    format_opportunity
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# GEMINI ERROR HANDLING
# ============================================================

def is_temporary_gemini_error(error):

    error_text = str(error).upper()

    temporary_markers = [
        "503",
        "UNAVAILABLE",
        "SERVICE UNAVAILABLE",
        "HIGH DEMAND",
        "TEMPORARILY UNAVAILABLE",
        "INTERNAL SERVER ERROR"
    ]

    return any(
        marker in error_text
        for marker in temporary_markers
    )


def is_quota_error(error):

    error_text = str(error).upper()

    quota_markers = [
        "429",
        "RESOURCE_EXHAUSTED",
        "QUOTA EXCEEDED",
        "RATE LIMIT"
    ]

    return any(
        marker in error_text
        for marker in quota_markers
    )


def generate_with_retry(
    client,
    model,
    contents,
    label="Gemini analysis",
    max_attempts=3
):

    last_error = None

    for attempt in range(
        1,
        max_attempts + 1
    ):

        try:

            response = client.models.generate_content(
                model=model,
                contents=contents
            )

            return response

        except Exception as error:

            last_error = error

            if is_quota_error(error):

                raise RuntimeError(
                    "Gemini quota/rate limit reached. "
                    "Please wait for the quota to reset "
                    "or check your Gemini API plan."
                ) from error


            if is_temporary_gemini_error(error):

                if attempt >= max_attempts:

                    raise RuntimeError(
                        f"{label} is temporarily unavailable "
                        f"after {max_attempts} attempts. "
                        "Gemini may currently be experiencing "
                        "high demand."
                    ) from error

                delay = 4 * (
                    2 ** (attempt - 1)
                )

                st.warning(
                    f"⚠️ Gemini is temporarily busy while "
                    f"performing {label}. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/{max_attempts})..."
                )

                time.sleep(delay)

                continue

            raise


    raise RuntimeError(
        f"{label} failed."
    ) from last_error


# ============================================================
# OPTIONAL GEMINI ANALYSIS
# ============================================================

def optional_gemini_analysis(
    client,
    model,
    contents,
    label
):

    try:

        response = generate_with_retry(
            client=client,
            model=model,
            contents=contents,
            label=label,
            max_attempts=3
        )

        return response.text

    except Exception as error:

        return (
            f"{label} was temporarily unavailable.\n\n"
            f"Reason: {error}\n\n"
            "This section was excluded from the current "
            "analysis rather than being fabricated."
        )


# ============================================================
# APPROVAL STATE
# ============================================================

if "approved_opportunities" not in st.session_state:

    st.session_state.approved_opportunities = []


if "declined_opportunities" not in st.session_state:

    st.session_state.declined_opportunities = []


if "pending_opportunities" not in st.session_state:

    st.session_state.pending_opportunities = []


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Market Intelligence Agent"
)

st.write(
    "Upload a stock or cryptocurrency chart "
    "for AI-powered market analysis."
)

st.divider()


# ============================================================
# OPPORTUNITY STATUS
# ============================================================

if st.session_state.approved_opportunities:

    st.success(
        f"✅ Approved opportunities: "
        f"{len(st.session_state.approved_opportunities)}"
    )


if st.session_state.declined_opportunities:

    st.info(
        f"❌ Declined opportunities: "
        f"{len(st.session_state.declined_opportunities)}"
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📷 Upload your chart screenshot",
    type=[
        "png",
        "jpg",
        "jpeg"
    ]
)


if uploaded_file is not None:

    st.subheader(
        "Chart Preview"
    )

    st.image(
        uploaded_file,
        use_container_width=True
    )

    st.divider()


    if st.button(
        "🔎 Analyze Market",
        use_container_width=True
    ):

        try:

            # ====================================================
            # GEMINI CLIENT
            # ====================================================

            client = genai.Client(
                api_key=st.secrets[
                    "GEMINI_API_KEY"
                ]
            )

            model_name = (
                "gemini-3.6-flash"
            )


            # ====================================================
            # IMAGE
            # ====================================================

            image_bytes = (
                uploaded_file.getvalue()
            )

            image_part = (
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=uploaded_file.type
                )
            )


            # ====================================================
            # ASSET IDENTIFICATION
            # ====================================================

            with st.spinner(
                "🔎 Identifying the asset..."
            ):

                identification_prompt = """
Look carefully at this financial chart.

Identify the asset shown.

Return ONLY the most likely trading symbol.

Examples:

BTC
ETH
SOL
AAPL
TSLA
NVDA

Do not provide an explanation.

If you cannot identify it,
return UNKNOWN.
"""

                identification_response = (
                    generate_with_retry(
                        client=client,
                        model=model_name,
                        contents=[
                            image_part,
                            identification_prompt
                        ],
                        label="asset identification"
                    )
                )

                asset_symbol = (
                    identification_response.text
                    .strip()
                    .upper()
                    .replace("/", "")
                    .replace("-", "")
                    .replace(" ", "")
                )


            # ====================================================
            # CRYPTO NORMALIZATION
            # ====================================================

            crypto_id = (
                normalize_crypto_id(
                    asset_symbol
                )
            )


            # ====================================================
            # MARKET DATA
            # ====================================================

            if crypto_id:

                try:

                    market_data = (
                        get_market_data(
                            crypto_id
                        )
                    )

                    market_context = f"""
LIVE MARKET DATA

Asset:
{asset_symbol}

Current market information:

{market_data}

IMPORTANT:

This information comes from an external
market-data source.

Treat it as factual market data,
not as a prediction.
"""

                except Exception as market_error:

                    market_context = f"""
LIVE MARKET DATA

The market-data request failed.

Error:
{market_error}

Do not invent current market data.
"""

            else:

                market_context = """
LIVE MARKET DATA

No supported cryptocurrency data
was retrieved.

If this is a stock or another asset,
do not invent current market data.

Base the analysis on the uploaded
chart and clearly identify this limitation.
"""


            # ====================================================
            # NEWS
            # ====================================================

            processed_news = []

            try:

                alpha_vantage_key = (
                    st.secrets[
                        "ALPHA_VANTAGE_API_KEY"
                    ]
                )

                news_symbol = asset_symbol

                if crypto_id:

                    news_symbol = (
                        f"CRYPTO:{asset_symbol}"
                    )

                news_data = (
                    get_market_news(
                        news_symbol,
                        alpha_vantage_key,
                        limit=10
                    )
                )

                processed_news = (
                    process_news_data(
                        news_data
                    )
                )

                formatted_news = (
                    format_news_for_ai(
                        processed_news
                    )
                )

                news_context = f"""
LIVE FINANCIAL NEWS

The following news items were retrieved
from an external financial-news source.

{formatted_news}

IMPORTANT:

Treat reported facts as external evidence.

Do not assume every headline is accurate.

Distinguish:

FACT
ANALYST OPINION
INFERENCE

Do not fabricate news.
"""

            except Exception as news_error:

                news_context = f"""
LIVE FINANCIAL NEWS

The news-data request failed.

Error:
{news_error}

Do not invent current news.

Clearly state that live news was unavailable.
"""


            # ====================================================
            # SENTIMENT
            # ====================================================

            try:

                sentiment_data = (
                    calculate_news_sentiment(
                        processed_news
                    )
                )

                sentiment_context = (
                    format_sentiment_for_ai(
                        sentiment_data
                    )
                )

            except Exception as sentiment_error:

                sentiment_context = f"""
MARKET SENTIMENT

The sentiment calculation failed.

Error:
{sentiment_error}

Do not invent market sentiment.
"""


            # ====================================================
            # MACRO
            # ====================================================

            try:

                macro_data = (
                    get_macro_data()
                )

                macro_context = (
                    format_macro_for_ai(
                        macro_data
                    )
                )

            except Exception as macro_error:

                macro_context = f"""
MACROECONOMIC DATA

The macroeconomic data request failed.

Error:
{macro_error}

Do not invent macroeconomic conditions.
"""


            # ====================================================
            # RESEARCH PROMPT
            # ====================================================

            research_prompt = (
                build_research_prompt(
                    asset_symbol
                )
            )


            # ====================================================
            # MULTI-TIMEFRAME
            # ====================================================

            with st.spinner(
                "⏱️ Analyzing multiple chart timeframes..."
            ):

                timeframe_prompt = (
                    build_timeframe_prompt(
                        asset_symbol
                    )
                )

                timeframe_text = (
                    optional_gemini_analysis(
                        client=client,
                        model=model_name,
                        contents=[
                            image_part,
                            timeframe_prompt
                        ],
                        label="multi-timeframe analysis"
                    )
                )


            # ====================================================
            # CATALYST ANALYSIS
            # ====================================================

            with st.spinner(
                "⚡ Analyzing catalysts and event risks..."
            ):

                catalyst_prompt = (
                    build_catalyst_prompt(
                        asset_symbol
                    )
                )

                catalyst_text = (
                    optional_gemini_analysis(
                        client=client,
                        model=model_name,
                        contents=[
                            catalyst_prompt
                        ],
                        label="catalyst and event analysis"
                    )
                )


            # ====================================================
            # MAIN ANALYSIS
            # ====================================================

            final_prompt = f"""
{research_prompt}

{market_context}

{news_context}

{sentiment_context}

{macro_context}

MULTI-TIMEFRAME ANALYSIS

{timeframe_text}

CATALYST AND EVENT-RISK ANALYSIS

{catalyst_text}


====================================================
ASSET
====================================================

{asset_symbol}


====================================================
OBSERVED EVIDENCE
====================================================

Identify evidence from:

- chart
- market data
- financial news
- sentiment
- macroeconomic conditions
- timeframe analysis
- catalyst analysis


====================================================
INFERENCES
====================================================

Explain reasonable conclusions derived
from the evidence.


====================================================
UNCERTAINTIES
====================================================

Identify what cannot be established reliably.


====================================================
BULLISH SCENARIO
====================================================

Explain evidence supporting the bullish case.


====================================================
NEUTRAL SCENARIO
====================================================

Explain evidence supporting the neutral,
range-bound or uncertain case.


====================================================
BEARISH SCENARIO
====================================================

Explain evidence supporting the bearish case.


====================================================
EVIDENCE RULES
====================================================

Do not fabricate:

- prices
- news
- events
- dates
- earnings
- economic data
- regulatory decisions
- technical patterns
- institutional activity
- analyst opinions

Clearly distinguish:

FACT
INFERENCE
ASSUMPTION
UNCERTAINTY


====================================================
EVIDENCE SCORING
====================================================

Score bullish and bearish evidence from 0 to 10.

0 = no evidence
1-2 = very weak
3-4 = weak
5-6 = moderate
7-8 = strong
9-10 = very strong


Return this exact JSON at the END:

{{
  "technical_bullish": 0,
  "technical_bearish": 0,

  "momentum_bullish": 0,
  "momentum_bearish": 0,

  "sentiment_bullish": 0,
  "sentiment_bearish": 0,

  "fundamental_bullish": 0,
  "fundamental_bearish": 0,

  "macro_bullish": 0,
  "macro_bearish": 0
}}


Use 0 when reliable evidence is unavailable.


====================================================
WHAT WOULD CHANGE THIS ANALYSIS
====================================================

List specific evidence, events or price behavior
that would materially change the assessment.
"""


            with st.spinner(
                "🤖 Completing market intelligence analysis..."
            ):

                response = (
                    generate_with_retry(
                        client=client,
                        model=model_name,
                        contents=[
                            image_part,
                            final_prompt
                        ],
                        label="main market intelligence analysis"
                    )
                )


            # ====================================================
            # ADVERSARIAL ANALYSIS
            # ====================================================

            adversarial_prompt = (
                build_adversarial_prompt(
                    asset_symbol=asset_symbol,
                    market_context=market_context,
                    news_context=news_context,
                    sentiment_context=sentiment_context,
                    macro_context=macro_context
                )
            )


            with st.spinner(
                "⚔️ Challenging the bullish and bearish cases..."
            ):

                adversarial_text = (
                    optional_gemini_analysis(
                        client=client,
                        model=model_name,
                        contents=[
                            adversarial_prompt
                        ],
                        label="bull vs bear adversarial analysis"
                    )
                )


            # ====================================================
            # DISPLAY RESULTS
            # ====================================================

            st.success(
                f"Asset identified: {asset_symbol}"
            )


            with st.expander(
                "📡 Market Data",
                expanded=False
            ):

                st.write(
                    market_context
                )


            with st.expander(
                "📰 Live Financial News",
                expanded=False
            ):

                if processed_news:

                    for index, article in enumerate(
                        processed_news,
                        start=1
                    ):

                        st.markdown(
                            f"### {index}. "
                            f"{article['title']}"
                        )

                        st.write(
                            f"**Source:** "
                            f"{article['source']}"
                        )

                        st.write(
                            f"**Published:** "
                            f"{article['published']}"
                        )

                        st.write(
                            f"**Sentiment:** "
                            f"{article['sentiment']}"
                        )

                        st.write(
                            f"**Sentiment Score:** "
                            f"{article['sentiment_score']}"
                        )

                        st.write(
                            f"**Relevance Score:** "
                            f"{article['relevance_score']}"
                        )

                        st.write(
                            article["summary"]
                        )

                        if article["url"]:

                            st.write(
                                article["url"]
                            )

                        st.divider()

                else:

                    st.info(
                        "No relevant live news was found."
                    )


            with st.expander(
                "📣 Market Sentiment",
                expanded=False
            ):

                st.write(
                    sentiment_context
                )


            with st.expander(
                "🌍 Macroeconomic Context",
                expanded=False
            ):

                st.write(
                    macro_context
                )


            st.divider()

            st.subheader(
                "⏱️ Multi-Timeframe Analysis"
            )

            st.write(
                timeframe_text
            )


            st.divider()

            st.subheader(
                "⚡ Catalyst & Event Risk"
            )

            st.write(
                catalyst_text
            )


            st.divider()

            st.subheader(
                "🤖 Market Intelligence Report"
            )

            st.write(
                response.text
            )


            st.divider()

            st.subheader(
                "⚔️ Bull vs Bear Adversarial Analysis"
            )

            st.write(
                adversarial_text
            )


            # ====================================================
            # EVIDENCE
            # ====================================================

            evidence_scores = (
                extract_evidence_scores(
                    response.text
                )
            )


            if evidence_scores:

                # =================================================
                # SCENARIO PROBABILITIES
                # =================================================

                probabilities = (
                    calculate_scenario_probabilities(
                        evidence_scores=evidence_scores,
                        adversarial_text=adversarial_text
                    )
                )


                # =================================================
                # CONFIDENCE
                # =================================================

                confidence = calculate_confidence(
                    evidence_scores=evidence_scores,
                    probabilities=probabilities,
                    adversarial_text=adversarial_text,
                    market_context=market_context,
                    news_context=news_context,
                    sentiment_context=sentiment_context,
                    macro_context=macro_context
                )


                # =================================================
                # PROBABILITY DISPLAY
                # =================================================

                st.divider()

                st.subheader(
                    "📊 Evidence-Weighted "
                    "Scenario Probabilities"
                )


                col1, col2, col3 = (
                    st.columns(3)
                )


                with col1:

                    st.metric(
                        "🐂 Bullish",
                        f"{probabilities['Bullish']}%"
                    )


                with col2:

                    st.metric(
                        "⚖️ Neutral",
                        f"{probabilities['Neutral']}%"
                    )


                with col3:

                    st.metric(
                        "🐻 Bearish",
                        f"{probabilities['Bearish']}%"
                    )


                st.caption(
                    "These are evidence-weighted scenarios, "
                    "not guaranteed future outcomes."
                )


                # =================================================
                # OPPORTUNITY ENGINE
                # =================================================

                opportunity = build_opportunity(
                    asset_symbol=asset_symbol,
                    scenario_probabilities=probabilities,
                    confidence_score=confidence["score"],
                    reason=(
                        "The setup is supported by the "
                        "combined market intelligence, "
                        "evidence scoring and adversarial "
                        "Bull/Bear analysis."
                    )
                )


                actionable = (
                    get_actionable_opportunities(
                        [opportunity],
                        minimum_score=65
                    )
                )


                # =================================================
                # OPPORTUNITY CARD
                # =================================================

                st.divider()

                st.subheader(
                    "🎯 Market Opportunity"
                )


                if actionable:

                    selected_opportunity = (
                        actionable[0]
                    )

                    st.markdown(
                        format_opportunity(
                            selected_opportunity
                        )
                    )


                    st.warning(
                        "⚠️ This is an AI-generated "
                        "market opportunity for your review. "
                        "It is NOT an automatic trade."
                    )


                    # =================================================
                    # APPROVAL CONTROLS
                    # =================================================

                    approve_col, decline_col = (
                        st.columns(2)
                    )


                    with approve_col:

                        approve = st.button(
                            "✅ APPROVE",
                            key=(
                                f"approve_"
                                f"{asset_symbol}"
                            ),
                            use_container_width=True
                        )


                    with decline_col:

                        decline = st.button(
                            "❌ DECLINE",
                            key=(
                                f"decline_"
                                f"{asset_symbol}"
                            ),
                            use_container_width=True
                        )


                    if approve:

                        selected_opportunity[
                            "status"
                        ] = "APPROVED"


                        st.session_state\
                            .approved_opportunities\
                            .append(
                                selected_opportunity
                            )


                        st.success(
                            f"✅ {asset_symbol} opportunity "
                            "approved."
                        )


                        st.info(
                            "Approval is recorded only. "
                            "No trade execution is connected "
                            "to this button yet."
                        )


                    elif decline:

                        selected_opportunity[
                            "status"
                        ] = "DECLINED"


                        st.session_state\
                            .declined_opportunities\
                            .append(
                                selected_opportunity
                            )


                        st.info(
                            f"❌ {asset_symbol} opportunity "
                            "declined."
                        )


                else:

                    st.info(
                        "No sufficiently strong actionable "
                        "opportunity was identified."
                    )


                # =================================================
                # CONFIDENCE
                # =================================================

                st.divider()

                st.subheader(
                    "🎯 Evidence Confidence"
                )


                confidence_col1, confidence_col2 = (
                    st.columns(2)
                )


                with confidence_col1:

                    st.metric(
                        "Evidence Confidence",
                        f"{confidence['score']}/100"
                    )


                with confidence_col2:

                    st.metric(
                        "Confidence Level",
                        confidence["label"]
                    )


                st.progress(
                    int(
                        max(
                            0,
                            min(
                                100,
                                confidence["score"]
                            )
                        )
                    )
                )


                st.write(
                    format_confidence_report(
                        confidence
                    )
                )


                # =================================================
                # EVIDENCE DETAILS
                # =================================================

                with st.expander(
                    "🔬 View Evidence Scores",
                    expanded=False
                ):

                    for key, value in (
                        evidence_scores.items()
                    ):

                        st.write(
                            f"**{key}:** {value}/10"
                        )


            else:

                st.warning(
                    "The AI did not return usable "
                    "evidence scores, so scenario "
                    "probabilities and opportunity "
                    "scoring could not be calculated."
                )


        # ========================================================
        # ERROR HANDLING
        # ========================================================

        except Exception as error:

            if is_quota_error(error):

                st.error(
                    "🚫 Gemini API quota has been reached. "
                    "Please wait for the quota to reset "
                    "or check your Gemini API plan."
                )

            elif is_temporary_gemini_error(error):

                st.error(
                    "⚠️ Gemini is currently experiencing "
                    "high demand. The app retried the "
                    "request but Gemini remained unavailable."
                )

            else:

                st.error(
                    f"Analysis failed: {error}"
                )


# ============================================================
# NO CHART
# ============================================================

else:

    st.info(
        "Upload a chart screenshot above to begin."
    )
