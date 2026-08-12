import streamlit as st
from research_engine import build_research_prompt
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

                prompt = build_research_prompt(
    "the asset shown in the uploaded chart"
                )

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
