# pages/page3.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import show_header

def create_simple_bar(df, title, color='#3498db'):
    """Create a simplified bar chart showing platform usage."""
    summary = df.groupby('platform').agg({
        'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
    }).reset_index().sort_values('ms_played', ascending=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary['ms_played'],
        y=summary['platform'],
        text=[f"{h:.1f}h" for h in summary['ms_played']],
        textposition='auto',
        marker_color=color,
        marker=dict(line=dict(width=0)),
        orientation='h',
        hovertemplate="%{y}<br>%{x:.1f} hours<extra></extra>"
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis_title="Hours Listened",
        yaxis_title=None,
        margin=dict(t=40, b=20, l=20, r=20),
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        bargap=0.3
    )
     
    return fig

def create_platform_timeline(df):
    """Create a line chart showing platform usage over time."""
    # Resample by month and pivot for platforms
    monthly = df.groupby([pd.Grouper(key='ts', freq='M'), 'platform']).agg({
        'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
    }).reset_index()
    
    # Pivot the data for plotting
    pivot_data = monthly.pivot(index='ts', columns='platform', values='ms_played').fillna(0)
    
    # Create the line chart
    fig = go.Figure()
    
    colors = {
        'android': '#a4c639',
        'ios': '#a2aaad',
        'osx': '#555555',
        'windows': '#00a4ef',
        'web player': '#1db954',
        'linux': '#dd4814'
    }
    
    for platform in pivot_data.columns:
        fig.add_trace(go.Scatter(
            x=pivot_data.index,
            y=pivot_data[platform],
            name=platform.title(),
            mode='lines',
            line=dict(width=2, color=colors.get(platform, '#3498db')),
            hovertemplate="%{x}<br>%{y:.1f} hours<extra></extra>"
        ))
    
    fig.update_layout(
        title="Platform Usage Over Time",
        showlegend=True,
        xaxis_title=None,
        yaxis_title="Hours Listened",
        margin=dict(t=40, b=20, l=20, r=20),
        height=400,
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
    """Display platform usage patterns."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("How Do You Listen?")
    
    df = st.session_state.df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    
    try:
        # Overall Platform Usage
        st.subheader("Your Platform Usage")
        fig_platforms = create_simple_bar(df, "Total Listening Time by Platform", '#e67e22')
        st.plotly_chart(fig_platforms, use_container_width=True)
        
        # Calculate and display primary platform
        platform_hours = df.groupby('platform').agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60)
        }).reset_index()
        
        primary_platform = platform_hours.loc[platform_hours['ms_played'].idxmax()]
        platform_percentage = (primary_platform['ms_played'] / platform_hours['ms_played'].sum() * 100)
        
        st.markdown(f"📱 Your primary listening platform is **{primary_platform['platform'].upper()}** "
                   f"with **{platform_percentage:.1f}%** of your total listening time")
        
        st.divider()
        
        # Platform Usage Over Time
        st.subheader("Platform Usage Trends")
        fig_timeline = create_platform_timeline(df)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Recent Platform Usage
        st.subheader("Recent Platform Usage")
        latest_month = df['ts'].max().strftime('%B %Y')
        recent_df = df[df['ts'].dt.to_period('M') == df['ts'].max().to_period('M')]
        
        recent_platforms = recent_df.groupby('platform').agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60)
        }).reset_index().sort_values('ms_played', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Most Used Platform",
                recent_platforms.iloc[0]['platform'].upper(),
                f"{recent_platforms.iloc[0]['ms_played']:.1f} hours"
            )
        with col2:
            if len(recent_platforms) > 1:
                st.metric(
                    "Second Most Used",
                    recent_platforms.iloc[1]['platform'].upper(),
                    f"{recent_platforms.iloc[1]['ms_played']:.1f} hours"
                )
        
        # Mobile vs Desktop Analysis
        mobile_platforms = ['android', 'ios']
        desktop_platforms = ['windows', 'osx', 'linux']
        
        mobile_hours = df[df['platform'].isin(mobile_platforms)]['ms_played'].sum() / (1000 * 60 * 60)
        desktop_hours = df[df['platform'].isin(desktop_platforms)]['ms_played'].sum() / (1000 * 60 * 60)
        
        st.divider()
        st.subheader("Mobile vs Desktop")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mobile Listening", f"{mobile_hours:.1f} hours")
        with col2:
            st.metric("Desktop Listening", f"{desktop_hours:.1f} hours")
        
        # Calculate the ratio
        total_hours = mobile_hours + desktop_hours
        mobile_pct = (mobile_hours / total_hours * 100) if total_hours > 0 else 0
        
        st.markdown(f"📊 You spend **{mobile_pct:.1f}%** of your time listening on mobile devices "
                   f"and **{100-mobile_pct:.1f}%** on desktop platforms")
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")