import streamlit as st
from utils.helpers import set_page_config
from pages import page1, page2

def main():
    """Main application entry point."""
    set_page_config()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Page 1", "Page 2"]
    )
    
    # Route to appropriate page
    if page == "Page 1":
        page1.show()
    elif page == "Page 2":
        page2.show()

if __name__ == "__main__":
    main()
