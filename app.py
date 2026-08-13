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
This information comes from an external market-data source.
Treat it as factual market data, not as a prediction.
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

No supported cryptocurrency data was retrieved.

If this is a stock or another asset, do not invent
current market data.

Base the analysis on the uploaded chart and clearly
identify the limitation.
"""


                # ------------------------------------------------
                # SECOND AI PASS:
                # FULL RESEARCH ANALYSIS
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
Things directly visible in the chart or supplied market data.

2. INFERENCES
Reasonable conclusions derived from the evidence.

3. UNCERTAINTIES
Things that cannot be established reliably.

4. BULLISH SCENARIO
Explain the conditions that could support this scenario.

5. NEUTRAL / RANGE SCENARIO
Explain the conditions that could support this scenario.

6. BEARISH SCENARIO
Explain the conditions that could support this scenario.

7. SCENARIO PROBABILITIES
Assign estimated probabilities to the three scenarios.

The three probabilities must total approximately 100%.

These are NOT predictions or guarantees.

They are evidence-weighted analytical estimates.

Do not fabricate news, prices, events, institutional activity,
economic data, or sentiment.

If information is unavailable, explicitly say so.

End with:

WHAT WOULD CHANGE THIS ANALYSIS

List the specific new evidence or price behavior that would
cause the assessment to change.
"""


                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        image_part,
                        final_prompt
                    ]
                )


                # ------------------------------------------------
                # DISPLAY RESULTS
                # ------------------------------------------------

                st.success(
                    f"Asset identified: {asset_symbol}"
                )

                if market_context:

                    with st.expander(
                        "📡 Market Data Retrieved",
                        expanded=False
                    ):

                        st.write(
                            market_context
                        )


                st.divider()

                st.subheader(
                    "🤖 Market Intelligence Report"
                )

                st.write(
                    response.text
                )


            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


else:

    st.info(
        "Upload a chart screenshot above to begin."
                )                    
                
