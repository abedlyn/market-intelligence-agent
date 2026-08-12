import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Market Intelligence Agent")

st.write(
    "Upload a stock or cryptocurrency chart for AI analysis."
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
            "🤖 AI is analyzing the chart..."
        ):

            try:

                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                image_bytes = uploaded_file.getvalue()

                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=uploaded_file.type
                )

                prompt = """
You are a financial chart analysis assistant.

Analyze the uploaded chart carefully.

Identify, if possible:

1. Asset or trading pair
2. Timeframe
3. Current trend
4. Market structure
5. Support levels
6. Resistance levels
7. Momentum
8. Volume behavior
9. Breakouts or breakdowns
10. Candlestick patterns
11. Technical patterns
12. Bullish evidence
13. Bearish evidence
14. Important uncertainties

IMPORTANT:

Do not claim to know the future.

Do not present your analysis as financial advice.

Do not invent information that cannot be observed from the chart.

Clearly distinguish what is visible from what is inferred.

Give a clear explanation of your reasoning.
"""

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        image_part,
                        prompt
                    ]
                )

                st.subheader("🤖 AI Chart Analysis")

                st.write(response.text)

            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )

else:

    st.info(
        "Upload a chart screenshot above to begin."
                )                
