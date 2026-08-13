import streamlit as st
from google import genai
from google.genai import types

from research_engine import (
    build_research_prompt,
    normalize_crypto_id
)

from market_data import get_market_data

from evidence_engine import (
    extract_evidence_scores,
    build_evidence_summary,
    format_probability_report
)


st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Market Intelligence Agent")

st.write(
    "Upload a stock or cryptocurrency chart for AI-powered market analysis."
)

st.divider()


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
            "🤖 AI is analyzing the chart and gathering market data..."
        ):

            try:

                # ------------------------------------------------
                # CONNECT TO GEMINI
                # ------------------------------------------------

                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )


                # ------------------------------------------------
                # READ IMAGE
                # ------------------------------------------------

                image_bytes = uploaded_file.getvalue()

                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=uploaded_file.type
                )


                # ------------------------------------------------
                # FIRST AI PASS:
                # IDENTIFY THE ASSET
                # ------------------------------------------------

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


                identification_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        image_part,
                        identification_prompt
                    ]
                )


                asset_symbol = (
                    identification_response.text
                    .strip()
                    .upper()
                    .replace("/", "")
                    .replace("-", "")
                    .replace(" ", "")
                )


                # ------------------------------------------------
                # NORMALIZE CRYPTO SYMBOL
                # ------------------------------------------------

                crypto_id = normalize_crypto_id(
                    asset_symbol
                )


                # ------------------------------------------------
                # GET LIVE CRYPTO MARKET DATA
                # ------------------------------------------------

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


                # ------------------------------------------------
                # BUILD RESEARCH PROMPT
                # ------------------------------------------------

                research_prompt = build_research_prompt(
                    asset_symbol
                )


                final_prompt = f"""
{research_prompt}

{market_context}


ADDITIONAL INSTRUCTIONS

You are analyzing:

{asset_symbol}


Separate your conclusions into:

1. OBSERVED EVIDENCE

Things directly visible in the chart
or supplied market data.


2. INFERENCES

Reasonable conclusions derived
from the evidence.


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


7. SCENARIO PROBABILITIES

You may discuss your initial assessment,
but the final displayed probabilities
will be calculated separately by the
evidence-scoring engine.


IMPORTANT:

These probabilities are NOT predictions
or guarantees.

They are evidence-weighted analytical
estimates.

Do not fabricate news, prices, events,
institutional activity, economic data,
or sentiment.

If information is unavailable,
explicitly say so.


EVIDENCE SCORING

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


End with:

WHAT WOULD CHANGE THIS ANALYSIS

List the specific new evidence or
price behavior that would cause the
assessment to change.
"""


                # ------------------------------------------------
                # FINAL AI ANALYSIS
                # ------------------------------------------------

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        image_part,
                        final_prompt
                    ]
                )


                # ------------------------------------------------
                # DISPLAY ASSET
                # ------------------------------------------------

                st.success(
                    f"Asset identified: {asset_symbol}"
                )


                # ------------------------------------------------
                # DISPLAY MARKET DATA
                # ------------------------------------------------

                if market_context:

                    with st.expander(
                        "📡 Market Data Retrieved",
                        expanded=False
                    ):

                        st.write(
                            market_context
                        )


                # ------------------------------------------------
                # DISPLAY AI REPORT
                # ------------------------------------------------

                st.divider()

                st.subheader(
                    "🤖 Market Intelligence Report"
                )

                st.write(
                    response.text
                )


                # ------------------------------------------------
                # EVIDENCE SCORING ENGINE
                # ------------------------------------------------

                evidence_scores = extract_evidence_scores(
                    response.text
                )


                if evidence_scores:

                    evidence_result = build_evidence_summary(
                        **evidence_scores
                    )


                    st.divider()

                    st.subheader(
                        "📊 Evidence-Weighted Scenario Probabilities"
                    )


                    probabilities = (
                        evidence_result["probabilities"]
                    )


                    st.write(
                        format_probability_report(
                            probabilities
                        )
                    )


                    # --------------------------------------------
                    # SHOW RAW EVIDENCE SCORES
                    # --------------------------------------------

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
                            "Neutral baseline score:",
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
                        "These percentages are calculated "
                        "from evidence scores returned by "
                        "the AI. They are analytical scenario "
                        "estimates, not predictions."
                    )


                else:

                    st.warning(
                        "The AI did not return usable "
                        "evidence scores, so evidence-weighted "
                        "probabilities could not be calculated."
                    )


            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


else:

    st.info(
        "Upload a chart screenshot above to begin."
)

                
