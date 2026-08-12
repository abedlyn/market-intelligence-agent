import streamlit as st
from google import genai

st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Market Intelligence Agent")
st.write("Upload a stock or cryptocurrency chart for AI analysis.")

uploaded_file = st.file_uploader(
    "📷 Upload your chart screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    st.subheader("Chart Preview")
    st.image(uploaded_file, use_container_width=True)

    if st.button("🔎 Analyze Market", use_container_width=True):

        with st.spinner("AI is analyzing the chart..."):

            try:
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {
                            "inline_data": {
                                "mime_type": uploaded_file.type,
                                "data": image_bytes
                            }
                        },
                        """
Analyze this financial chart carefully.

Identify, if possible:
- Asset and trading pair
- Timeframe
- Current trend
- Market structure
- Support and resistance
- Momentum
- Volume behavior
- Breakouts or breakdowns
- Important technical patterns
- Bullish evidence
- Bearish evidence
- Important uncertainties

Do NOT claim to predict the future.
Do NOT invent information that cannot be seen.

Present the result clearly and explain your reasoning.
"""
                    ]
                )

                st.subheader("🤖 AI Chart Analysis")
                st.write(response.text)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

else:
    st.info("Upload a chart screenshot above to begin.")                        {
                            "inline_data": {
                                "mime_type": uploaded_file.type,
                                "data": image_bytes
                            }
                        },
                        """
                        Analyze this financial chart carefully.

                        Identify, if possible:
                        - Asset and trading pair
                        - Timeframe
                        - Current trend
                        - Market structure
                        - Support and resistance
                        - Momentum
                        - Volume behavior
                        - Breakouts or breakdowns
                        - Important technical patterns
                        - Bullish evidence
                        - Bearish evidence
                        - Important uncertainties

                        Do NOT claim to predict the future.
                        Do NOT invent information that cannot be seen.

                        Present the result clearly and explain your reasoning.
                        """
                    ]
                )

                st.subheader("🤖 AI Chart Analysis")
                st.write(response.text)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

else:
    st.info("Upload a chart screenshot above to begin.")            "The AI research engine will be connected here next."
        )

else:

    st.info(
        "Upload a chart screenshot above to begin."
  )
