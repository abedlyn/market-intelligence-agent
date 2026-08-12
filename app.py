import streamlit as st

st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Market Intelligence Agent")
st.write(
    "Upload a stock or cryptocurrency chart for structured market analysis."
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

    st.subheader("Analysis")

    if st.button("🔎 Analyze Market", use_container_width=True):

        st.info(
            "The AI research engine will be connected here next."
        )

else:

    st.info(
        "Upload a chart screenshot above to begin."
  )
