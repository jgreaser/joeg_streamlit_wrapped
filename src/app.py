# app.py
import streamlit as st
import json
import pandas as pd
from utils.helpers import set_page_config
from utils.file_validator import process_spotify_zip
from pages import page1, page2, page3, page4, page5

def initialize_session_state():
    """Initialize session state variables."""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "data_overview"

def main():
    """Main application entry point."""
    set_page_config()
    initialize_session_state()
    
    # Clean sidebar with icons
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stRadio"] {margin: -1rem 0 -1rem 0;}
            [data-testid="stRadio"] > label {display: none;}
            [data-testid="stRadio"] > div {display: flex; flex-direction: column; gap: 0.5rem;}
            [data-testid="stRadio"] > div > label {
                padding: 0.5rem;
                border-radius: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
            }
            [data-testid="stRadio"] > div > label:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.data_loaded:
            selected = st.radio(
                "Navigation",
                [
                    "📊 Overview",
                    "🎵 Songs",
                    "👤 Artists",
                    "⏰ Time",
                    "📱 Platform"
                ],
                key="navigation",
                label_visibility="collapsed",
                horizontal=False,
            )
            
            with st.expander("🔧 Debug Info"):
                st.write(f"Data loaded: {st.session_state.data_loaded}")
                st.write(f"Current page: {selected}")
                if st.session_state.df is not None:
                    st.write(f"DataFrame shape: {st.session_state.df.shape}")
    
    st.title("JoeG Streamlit Wrapped")
    
    # Display the selected page
    if st.session_state.data_loaded:
        if "Overview" in selected:
            show_data_overview()
        elif "Songs" in selected:
            page1.show()
        elif "Artists" in selected:
            page2.show()
        elif "Time" in selected:
            page4.show()
        elif "Platform" in selected:
            page5.show()
    else:
        show_data_upload()

def show_data_upload():
    """Handle initial file upload."""
    st.write("👋 Welcome! Please upload your Spotify data file.")
    
    with st.expander("ℹ️ How to get your data"):
        st.markdown("""
            1. Go to your [Spotify Account Privacy Settings](https://www.spotify.com/account/privacy/)
            2. Request your extended streaming history
            3. Wait for the email (can take a few days)
            4. Download and upload the my_spotify_data.zip file
        """)
    
    uploaded_file = st.file_uploader(
        "Upload my_spotify_data.zip",
        type=['zip'],
        help="Upload the zip file from your Spotify data download",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        with st.spinner('Processing your Spotify history...'):
            try:
                result = process_spotify_zip(uploaded_file)
                
                if result['is_valid']:
                    df = result['df']
                    st.session_state.df = df
                    st.session_state.data_loaded = True
                    st.rerun()
                else:
                    st.error(f"❌ Invalid file: {result['error']}")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")

def show_data_overview():
    """Show data overview and statistics."""
    st.success("✅ Spotify history loaded and ready to analyze!")
    
    if st.button("Load Different File"):
        st.session_state.data_loaded = False
        st.session_state.df = None
        st.rerun()
    
    st.subheader("Data Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Streams", len(st.session_state.df))
    with col2:
        date_range = f"{st.session_state.df['ts'].min().year} - {st.session_state.df['ts'].max().year}"
        st.metric("Date Range", date_range)
    with col3:
        total_hours = st.session_state.df['ms_played'].sum() / (1000 * 60 * 60)
        st.metric("Total Hours", f"{total_hours:.1f}")
    
    st.subheader("Preview")
    display_df = st.session_state.df[[
        'ts', 
        'master_metadata_track_name',
        'master_metadata_album_artist_name',
        'ms_played'
    ]].head()
    display_df.columns = ['Timestamp', 'Track', 'Artist', 'MS Played']
    st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()