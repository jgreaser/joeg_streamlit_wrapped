# pages/page1.py
import streamlit as st
import pandas as pd
from utils.helpers import show_header

def categorize_platform(platform):
    """Categorize platforms into Mobile, Desktop, or Web."""
    if platform in ['android', 'ios']:
        return 'Mobile'
    elif platform in ['windows', 'osx', 'linux']:
        return 'Desktop'
    return 'Web'

def show():
    """Display the top songs analysis."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("Top Songs Analysis")
    
    # Get the dataframe from session state
    df = st.session_state.df.copy()  # Create a copy to avoid modifying original
    
    try:
        # Convert timestamp to datetime if not already
        df['ts'] = pd.to_datetime(df['ts'])
        
        # Add device type categorization
        df['device_type'] = df['platform'].apply(categorize_platform)
        
        # Create filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # Year filter
            years = sorted(df['ts'].dt.year.unique())
            selected_year = st.selectbox(
                "Select Year",
                ["All Years"] + list(years)
            )
            
        with col2:
            # Platform filter
            devices = sorted(df['device_type'].unique())
            selected_device = st.selectbox(
                "Device Type",
                ["All Devices"] + list(devices)
            )
            
        with col3:
            # Filter for skipped songs
            include_skipped = st.checkbox("Include Skipped Songs", value=False)
            
        with col4:
            # Minimum play time filter (in seconds)
            min_seconds = st.number_input(
                "Minimum Seconds Played",
                min_value=0,
                value=30,
                help="Filter out songs played less than this many seconds"
            )
            
        # Apply filters
        if selected_year != "All Years":
            df = df[df['ts'].dt.year == selected_year]
            
        if selected_device != "All Devices":
            df = df[df['device_type'] == selected_device]
            
        if not include_skipped:
            df = df[~df['skipped']]
            
        df = df[df['ms_played'] >= (min_seconds * 1000)]
            
        # Group by song and calculate metrics
        songs_df = df.groupby(
            ['master_metadata_track_name', 'master_metadata_album_artist_name', 'master_metadata_album_album_name']
        ).agg({
            'ms_played': 'sum',
            'ts': 'count',
            'skipped': 'sum',
            'shuffle': 'mean',  # This will give us % of shuffled plays
            'device_type': lambda x: ', '.join(sorted(x.unique()))  # List of devices used
        }).reset_index()
        
        # Rename and calculate columns
        songs_df = songs_df.rename(columns={
            'master_metadata_track_name': 'Song',
            'master_metadata_album_artist_name': 'Artist',
            'master_metadata_album_album_name': 'Album',
            'ts': 'Play Count',
            'shuffle': 'Shuffle %',
            'skipped': 'Times Skipped',
            'device_type': 'Devices Used'
        })
        
        songs_df['Minutes Played'] = (songs_df['ms_played'] / (1000 * 60)).round(2)
        songs_df['Shuffle %'] = (songs_df['Shuffle %'] * 100).round(1)
        
        # Sort by play count descending
        songs_df = songs_df.sort_values('Play Count', ascending=False)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Songs", len(songs_df))
        with col2:
            st.metric("Total Plays", songs_df['Play Count'].sum())
        with col3:
            total_hours = (songs_df['ms_played'].sum() / (1000 * 60 * 60)).round(2)
            st.metric("Total Hours", total_hours)
        with col4:
            avg_shuffle = (df['shuffle'].mean() * 100).round(1)
            st.metric("Shuffle %", f"{avg_shuffle}%")
        
        # Create title with applied filters
        title_filters = []
        if selected_year != "All Years":
            title_filters.append(str(selected_year))
        if selected_device != "All Devices":
            title_filters.append(selected_device)
        
        title = "Songs Ranking" + (f" ({', '.join(title_filters)})" if title_filters else "")
        st.subheader(title)
        
        # Format the table for display
        display_df = songs_df[[
            'Song', 'Artist', 'Album', 'Play Count', 
            'Minutes Played', 'Shuffle %', 'Times Skipped',
            'Devices Used'
        ]].copy()
        
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1  # Start index at 1
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Play Count": st.column_config.NumberColumn(format="%d"),
                "Minutes Played": st.column_config.NumberColumn(format="%.2f"),
                "Shuffle %": st.column_config.NumberColumn(format="%.1f%%"),
                "Times Skipped": st.column_config.NumberColumn(format="%d"),
                "Devices Used": st.column_config.TextColumn(help="Devices used to play this song")
            }
        )
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Please make sure your JSON file contains valid Spotify streaming history data.")