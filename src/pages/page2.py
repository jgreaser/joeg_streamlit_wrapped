# pages/page2.py
import streamlit as st
import pandas as pd
from utils.helpers import show_header

def show():
    """Display the top artists analysis."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("Top Artists Analysis")
    
    # Get the dataframe from session state
    df = st.session_state.df.copy()
    
    try:
        # Convert timestamp to datetime if not already
        df['ts'] = pd.to_datetime(df['ts'])
        
        # Create filters
        col1, col2, col3 = st.columns(3)
        with col1:
            # Year filter
            years = sorted(df['ts'].dt.year.unique())
            selected_year = st.selectbox(
                "Select Year",
                ["All Years"] + list(years)
            )
            
        with col2:
            # Filter for skipped songs
            include_skipped = st.checkbox("Include Skipped Songs", value=False)
            
        with col3:
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
            
        if not include_skipped:
            df = df[~df['skipped']]
            
        df = df[df['ms_played'] >= (min_seconds * 1000)]
        
        # Group by artist
        artists_df = df.groupby('master_metadata_album_artist_name').agg({
            'master_metadata_track_name': 'nunique',  # Count unique songs
            'ms_played': 'sum',
            'ts': 'count',
            'skipped': 'sum',
            'shuffle': 'mean',
            'master_metadata_album_album_name': 'nunique'  # Count unique albums
        }).reset_index()
        
        # Rename columns
        artists_df = artists_df.rename(columns={
            'master_metadata_album_artist_name': 'Artist',
            'master_metadata_track_name': 'Unique Songs',
            'ts': 'Total Plays',
            'skipped': 'Times Skipped',
            'shuffle': 'Shuffle %',
            'master_metadata_album_album_name': 'Albums Played'
        })
        
        # Calculate additional metrics
        artists_df['Hours Played'] = (artists_df['ms_played'] / (1000 * 60 * 60)).round(2)
        artists_df['Avg Minutes Per Play'] = (
            artists_df['ms_played'] / (1000 * 60) / artists_df['Total Plays']
        ).round(2)
        artists_df['Shuffle %'] = (artists_df['Shuffle %'] * 100).round(1)
        
        # Sort by total plays descending
        artists_df = artists_df.sort_values('Total Plays', ascending=False)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Artists", len(artists_df))
        with col2:
            st.metric("Total Plays", artists_df['Total Plays'].sum())
        with col3:
            total_hours = artists_df['Hours Played'].sum().round(2)
            st.metric("Total Hours", total_hours)
        with col4:
            avg_songs_per_artist = artists_df['Unique Songs'].mean().round(1)
            st.metric("Avg Songs/Artist", avg_songs_per_artist)
        
        # Display the sorted table
        st.subheader(f"Artist Ranking {'(' + str(selected_year) + ')' if selected_year != 'All Years' else ''}")
        
        # Format table for display
        display_df = artists_df[[
            'Artist', 
            'Total Plays', 
            'Hours Played',
            'Unique Songs',
            'Albums Played',
            'Avg Minutes Per Play',
            'Times Skipped',
            'Shuffle %'
        ]].copy()
        
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1  # Start index at 1
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Total Plays": st.column_config.NumberColumn(format="%d"),
                "Hours Played": st.column_config.NumberColumn(format="%.2f"),
                "Unique Songs": st.column_config.NumberColumn(format="%d"),
                "Albums Played": st.column_config.NumberColumn(format="%d"),
                "Avg Minutes Per Play": st.column_config.NumberColumn(format="%.2f"),
                "Times Skipped": st.column_config.NumberColumn(format="%d"),
                "Shuffle %": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Add a bar chart of top 10 artists by plays
        st.subheader("Top 10 Artists by Plays")
        top_10_artists = display_df.head(10)
        st.bar_chart(
            top_10_artists.set_index('Artist')['Total Plays'],
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Please make sure your JSON file contains valid Spotify streaming history data.")