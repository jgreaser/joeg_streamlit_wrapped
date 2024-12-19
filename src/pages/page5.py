# pages/page5.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import show_header

def categorize_platform(platform):
    """Categorize platforms into Mobile, Desktop, or Web."""
    if platform in ['android', 'ios']:
        return 'Mobile'
    elif platform in ['windows', 'osx', 'linux']:
        return 'Desktop'
    return 'Web'

def create_device_timeline(df):
    """Create a line chart showing device type usage over time."""
    monthly = df.groupby([pd.Grouper(key='ts', freq='M'), 'device_type']).agg({
        'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
    }).reset_index()
    
    fig = px.line(monthly, x='ts', y='ms_played', color='device_type',
                  title='Device Usage Over Time',
                  labels={'ms_played': 'Hours Played', 'ts': 'Date', 'device_type': 'Device Type'})
    
    fig.update_layout(
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def show():
    """Display device type usage patterns."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("How Do You Listen?")
    
    # Get the base dataframe
    df = st.session_state.df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    df['device_type'] = df['platform'].apply(categorize_platform)
    
    try:
        # Create filters in columns like page1.py
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
            time_period = str(selected_year)
        else:
            time_period = f"{min(years)}-{max(years)}"
            
        if not include_skipped:
            df = df[~df['skipped']]
            
        df = df[df['ms_played'] >= (min_seconds * 1000)]
        
        # Calculate device type metrics
        device_stats = df.groupby('device_type').agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60),  # Hours
            'ts': 'count',  # Play count
            'master_metadata_track_name': 'nunique',  # Unique tracks
            'skipped': 'sum',  # Skipped count
            'shuffle': 'mean'  # Shuffle percentage
        }).reset_index()
        
        device_stats.columns = ['Device Type', 'Hours', 'Plays', 'Unique Tracks', 'Skipped', 'Shuffle %']
        
        # Calculate additional metrics
        device_stats['Avg Session (mins)'] = (device_stats['Hours'] * 60) / device_stats['Plays']
        device_stats['Skip Rate'] = (device_stats['Skipped'] / device_stats['Plays'] * 100)
        device_stats['Shuffle %'] = device_stats['Shuffle %'] * 100
        
        # Sort by hours played
        device_stats = device_stats.sort_values('Hours', ascending=False)
        
        # Overview visualization
        st.subheader(f"Device Usage Overview ({time_period})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart of usage distribution
            fig_pie = px.pie(
                device_stats,
                values='Hours',
                names='Device Type',
                title='Listening Time Distribution'
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            # Primary device stats
            if not device_stats.empty:
                primary_device = device_stats.iloc[0]
                total_hours = device_stats['Hours'].sum()
                
                st.metric("Primary Device", primary_device['Device Type'])
                st.metric("Hours on Primary", f"{primary_device['Hours']:.1f}")
                st.metric(
                    "% of Listening",
                    f"{(primary_device['Hours'] / total_hours * 100):.1f}%"
                )
        
        # Usage timeline (show for all views now)
        st.subheader("Usage Patterns")
        timeline_fig = create_device_timeline(df)
        st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Detailed comparison
        st.subheader("Device Comparison")
        comparison_df = device_stats[[
            'Device Type', 'Hours', 'Plays', 'Unique Tracks',
            'Avg Session (mins)', 'Skip Rate', 'Shuffle %'
        ]].copy()
        
        st.dataframe(
            comparison_df,
            use_container_width=True,
            column_config={
                "Hours": st.column_config.NumberColumn(format="%.1f"),
                "Plays": st.column_config.NumberColumn(format="%d"),
                "Unique Tracks": st.column_config.NumberColumn(format="%d"),
                "Avg Session (mins)": st.column_config.NumberColumn(format="%.1f"),
                "Skip Rate": st.column_config.NumberColumn(format="%.1f%%"),
                "Shuffle %": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Time of day analysis
        st.subheader(f"When Do You Use Each Device? ({time_period})")
        
        df['part_of_day'] = pd.cut(
            df['ts'].dt.hour,
            bins=[0, 6, 12, 18, 24],
            labels=['Night (12AM-6AM)', 'Morning (6AM-12PM)', 
                   'Afternoon (12PM-6PM)', 'Evening (6PM-12AM)']
        )
        
        time_device = df.groupby(['device_type', 'part_of_day']).agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60)
        }).reset_index()
        
        time_fig = px.bar(
            time_device,
            x='part_of_day',
            y='ms_played',
            color='device_type',
            title='Device Usage by Time of Day',
            labels={'ms_played': 'Hours Played', 'part_of_day': 'Time of Day', 'device_type': 'Device Type'}
        )
        
        time_fig.update_layout(
            height=400,
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(time_fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")