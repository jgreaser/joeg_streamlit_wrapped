import streamlit as st

def set_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="JoeG Streamlit Wrapped",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def show_header():
    """Display the application header."""
    st.title("JoeG Streamlit Wrapped")
    st.markdown("---")
