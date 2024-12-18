import streamlit as st
from ..utils.helpers import show_header
from ..services.data_service import DataService

def show():
    """Display the second page content."""
    show_header()
    
    st.header("Page 2")
    st.write("This is the content of page 2")
    
    # Add your page-specific content here
    with st.container():
        st.write("Add your widgets and content here")