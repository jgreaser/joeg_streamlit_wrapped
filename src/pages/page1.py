import streamlit as st
from ..utils.helpers import show_header
from ..services.data_service import DataService

def show():
    """Display the first page content."""
    show_header()
    
    st.header("Page 1")
    st.write("This is the content of page 1")
    
    # Add your page-specific content here
    with st.container():
        st.write("Add your widgets and content here")