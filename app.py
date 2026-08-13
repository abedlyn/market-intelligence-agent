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

from evidence_engine import (
    extract_evidence_scores,
    build_evidence_summary,
    format_probability_report
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
# APP HEADER
# ============================================================

st.title("📊 Market Intelligence Agent")

st.write(
    "Upload a stock or cryptocurrency chart for "
    "AI-powered market analysis."
)

st.divider()


# ============================================================
# CHART UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📷 Upload your chart screenshot",
    type=["png", "jpg", "jpeg"]
)


if uploaded_file is not None:

    st.subheader("Chart Preview")

    st.image(
        uploaded_file,
        use_container_width=True
    )

    st.divider()

    if st.button(
        "🔎 Analyze Market",
        use_container_width=True
    ):

        with st.spinner(
            "🤖 AI is analyzing the chart and gathering "
            "live market intelligence..."
        ):

            try:

                # ====================================================
                # CONNECT TO GEMINI
                # ====================================================

                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )


                # ====================================================
                # READ IMAGE
                # ====================================================

                image_bytes = uploaded_file.getvalue()

                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=uploaded_file.type
                )


                # ====================================================
                # IDENTIFY ASSET
                # ====================================================

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
Do not provide anything else.

If you cannot identify it, return UNKNOWN.
"""


                identification_response = (
                    client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            image_part,
                            identification_prompt
                        ]
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
                # NORMALIZE CRYPTO SYMBOL
                # ====================================================

                crypto_id = normalize_crypto_id(
                    asset_symbol
                )


                # ====================================================
                # LIVE MARKET DATA
                # ====================================================

                market_context = ""

                if crypto_id:

                    try:

                        market_data = get_market_data(
                            crypto_id
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
                # LIVE FINANCIAL NEWS
                # ====================================================

                news_context = ""

                try:

                    alpha_vantage_key = st.secrets[
                        "ALPHA_VANTAGE_API_KEY"
                    ]

                    news_symbol = asset_symbol

                    if crypto_id:

                        news_symbol = (
                            f"CRYPTO:{asset_symbol}"
                        )


                    # ------------------------------------------------
                    # RETRIEVE NEWS
                    # ------------------------------------------------

                    news_data = get_market_news(
                        news_symbol,
                        alpha_vantage_key,
                        limit=10
                    )


                    # ------------------------------------------------
                    # PROCESS NEWS
                    # ------------------------------------------------

                    processed_news = process_news_data(
                        news_data
                    )


                    # ------------------------------------------------
                    # FORMAT NEWS FOR AI
                    # ------------------------------------------------

                    formatted_news = format_news_for_ai(
                        processed_news
                    )


                    news_context = f"""
LIVE FINANCIAL NEWS

The following news items were retrieved
from an external financial-news source.

{formatted_news}

IMPORTANT:

Treat reported facts as external evidence.

Do not assume that every headline is accurate
or that every article represents market consensus.

Distinguish reported facts from analyst opinions
and from your own inference.

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
                # BUILD RESEARCH PROMPT
                # ====================================================

                research_prompt = build_research_prompt(
                    asset_symbol
                )


                # ====================================================
                # FINAL RESEARCH PROMPT
                # ====================================================

                final_prompt = f"""
{research_prompt}

{market_context}

{news_context}


ADDITIONAL INSTRUCTIONS

You are analyzing:

{asset_symbol}


Separate your conclusions into:


1. OBSERVED EVIDENCE

Things directly visible in the chart,
supplied market data, or retrieved news.


2. INFERENCES

Reasonable conclusions derived
from the available evidence.


3. UNCERTAINTIES

Things that cannot be established reliably.


4. BULLISH SCENARIO

Explain the conditions that could
support this scenario.


5. NEUTRAL / RANGE SCENARIO

Explain the conditions that could
support this scenario.


6. BEARISH SCENARIO

Explain the conditions that could
support this scenario.


7. SCENARIO ASSESSMENT

Explain which scenario currently has
the strongest evidence and why.

Do not treat this as a prediction.


IMPORTANT

Do NOT fabricate:

- news
- prices
- events
- institutional activity
- economic data
- sentiment
- analyst opinions

If information is unavailable,
explicitly say so.

Clearly distinguish:

FACT
INFERENCE
ASSUMPTION
UNCERTAINTY


====================================================
EVIDENCE SCORING
====================================================

After completing your analysis, assign
evidence strength scores from 0 to 10
for each category.

0 = no evidence
1-2 = very weak
3-4 = weak
5-6 = moderate
7-8 = strong
9-10 = very strong


Score BOTH bullish and bearish evidence.

Use this exact JSON format:

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


Return the JSON at the very end
of your response.

Do not invent evidence simply
to give a score.

If evidence is unavailable,
use 0.


====================================================
WHAT WOULD CHANGE THIS ANALYSIS
====================================================

List the specific new evidence or
price behavior that would cause the
assessment to change.
"""


                # ====================================================
                # FINAL AI ANALYSIS
                # ====================================================

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        image_part,
                        final_prompt
                    ]
                )


                # ====================================================
                # DISPLAY IDENTIFIED ASSET
                # ====================================================

                st.success(
                    f"Asset identified: {asset_symbol}"
                )


                # ====================================================
                # DISPLAY MARKET DATA
                # ====================================================

                with st.expander(
                    "📡 Market Data",
                    expanded=False
                ):

                    st.write(
                        market_context
                    )


                # ====================================================
                # DISPLAY PROCESSED NEWS
                # ====================================================

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


                # ====================================================
                # DISPLAY AI REPORT
                # ====================================================

                st.divider()

                st.subheader(
                    "🤖 Market Intelligence Report"
                )

                st.write(
                    response.text
                )


                # ====================================================
                # EVIDENCE SCORING ENGINE
                # ====================================================

                evidence_scores = (
                    extract_evidence_scores(
                        response.text
                    )
                )


                if evidence_scores:

                    evidence_result = (
                        build_evidence_summary(
                            **evidence_scores
                        )
                    )


                    st.divider()

                    st.subheader(
                        "📊 Evidence-Weighted "
                        "Scenario Probabilities"
                    )


                    probabilities = (
                        evidence_result[
                            "probabilities"
                        ]
                    )


                    st.write(
                        format_probability_report(
                            probabilities
                        )
                    )


                    # ------------------------------------------------
                    # EVIDENCE DETAILS
                    # ------------------------------------------------

                    with st.expander(
                        "🔬 View Evidence Scores",
                        expanded=False
                    ):

                        st.write(
                            "Bullish evidence score:",
                            evidence_result[
                                "bullish_score"
                            ]
                        )

                        st.write(
                            "Neutral / uncertainty score:",
                            evidence_result[
                                "neutral_score"
                            ]
                        )

                        st.write(
                            "Bearish evidence score:",
                            evidence_result[
                                "bearish_score"
                            ]
                        )

                        st.json(
                            evidence_scores
                        )


                    st.caption(
                        "These percentages are "
                        "evidence-weighted scenario "
                        "estimates. They are not predictions "
                        "or guarantees."
                    )


                else:

                    st.warning(
                        "The AI did not return usable "
                        "evidence scores, so "
                        "evidence-weighted probabilities "
                        "could not be calculated."
                    )


            # ========================================================
            # ERROR HANDLING
            # ========================================================

            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


# ================================================================
# NO CHART UPLOADED
# ================================================================

else:

    st.info(
        "Upload a chart screenshot above to begin."
)
