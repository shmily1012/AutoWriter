import streamlit as st

st.set_page_config(page_title="Novel System", page_icon="📚")

st.title("Hello novelist")
st.write(
    "Backend at `/ping` should return `{\"status\":\"ok\"}` when the FastAPI server is running."
)
