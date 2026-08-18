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

                processed_news = []

                try:

                    alpha_vantage_key = st.secrets[
                        "ALPHA_VANTAGE_API_KEY"
                    ]

                    news_symbol = asset_symbol

                    if crypto_id:

                        news_symbol = (
                            f"CRYPTO:{asset_symbol}"
                        )

                    news_data = get_market_news(
                        news_symbol,
                        alpha_vantage_key,
                        limit=10
                    )

                    processed_news = process_news_data(
                        news_data
                    )

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
                # MARKET SENTIMENT
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
               
