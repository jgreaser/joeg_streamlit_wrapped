# pages/page3.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import show_header

def show():
    """Display listening distribution analysis."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("Understanding Your Listening Distribution")
    
    df = st.session_state.df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    
    try:
        # Filter controls in a clean expander
        with st.expander("Filter Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                years = sorted(df['ts'].dt.year.unique())
                selected_year = st.selectbox(
                    "Select Year",
                    ["All Years"] + list(years)
                )
            
            with col2:
                min_seconds = st.number_input(
                    "Minimum Seconds Played",
                    min_value=0,
                    value=30
                )
                
            with col3:
                analysis_type = st.selectbox(
                    "Analyze by",
                    ["Artists", "Songs"]
                )
                
        # Apply filters
        if selected_year != "All Years":
            df = df[df['ts'].dt.year == selected_year]
        df = df[df['ms_played'] >= (min_seconds * 1000)]
        
        # Group data
        group_column = ('master_metadata_album_artist_name' if analysis_type == "Artists" 
                       else 'master_metadata_track_name')
        
        grouped_df = df.groupby(group_column).agg({
            'ms_played': 'sum',
            'ts': 'count'
        }).reset_index()
        
        grouped_df = grouped_df.rename(columns={
            group_column: 'Name',
            'ts': 'Play Count',
            'ms_played': 'Total Time (ms)'
        })
        
        # Calculate key metrics
        grouped_df['Hours'] = grouped_df['Total Time (ms)'] / (1000 * 60 * 60)
        total_hours = grouped_df['Hours'].sum()
        grouped_df = grouped_df.sort_values('Hours', ascending=True)
        grouped_df['Cumulative Hours'] = grouped_df['Hours'].cumsum()
        grouped_df['Percentage of Total'] = (grouped_df['Hours'] / total_hours * 100)
        grouped_df['Cumulative Percentage'] = (grouped_df['Cumulative Hours'] / total_hours * 100)
        
        # Key numbers for insights
        total_items = len(grouped_df)
        items_80_percent = len(grouped_df[grouped_df['Cumulative Percentage'] <= 80])
        top_20_percent_count = int(total_items * 0.2)
        
        # 1. Simple, clear message about concentration
        st.subheader("Your Listening is Highly Concentrated")
        st.markdown(f"""
        Out of your **{total_items:,} {analysis_type.lower()}**, just **{items_80_percent:,}** account for 
        **80%** of your listening time. That's only {(items_80_percent/total_items*100):.1f}% of your library!
        """)
        
        # 2. Clear visual of the concentration
        st.subheader("Top vs Rest Comparison")
        
        # Calculate metrics for top 20%
        top_20_hours = grouped_df.nlargest(top_20_percent_count, 'Hours')['Hours'].sum()
        rest_hours = total_hours - top_20_hours
        
        # Create simple bar chart comparing top 20% to rest
        comparison_data = pd.DataFrame({
            'Category': [f'Top 20% ({top_20_percent_count:,} {analysis_type.lower()})', 
                        f'Remaining 80% ({total_items - top_20_percent_count:,} {analysis_type.lower()})'],
            'Hours': [top_20_hours, rest_hours]
        })
        
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Bar(
            x=comparison_data['Category'],
            y=comparison_data['Hours'],
            text=[f"{h:.1f} hours<br>({h/total_hours*100:.1f}%)" for h in comparison_data['Hours']],
            textposition='auto',
            marker_color=['#2ecc71', '#95a5a6']  # Distinct colors for emphasis
        ))
        
        fig_comparison.update_layout(
            title=None,
            showlegend=False,
            xaxis_title=None,
            yaxis_title="Hours Played",
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # 3. Top 10 Detail
        st.subheader(f"Your Top 10 Most-Played {analysis_type}")
        
        # Get top 10 and calculate their percentage of total
        top_10 = grouped_df.nlargest(10, 'Hours')
        top_10['Percentage'] = (top_10['Hours'] / total_hours * 100)
        
        # Create horizontal bar chart for top 10
        fig_top10 = go.Figure()
        fig_top10.add_trace(go.Bar(
            y=top_10['Name'][::-1],  # Reverse order for proper sorting
            x=top_10['Hours'][::-1],
            orientation='h',
            text=[f"{h:.1f} hrs ({p:.1f}%)" for h, p in zip(top_10['Hours'][::-1], top_10['Percentage'][::-1])],
            textposition='auto',
            marker_color='#3498db'
        ))
        
        fig_top10.update_layout(
            title=None,
            showlegend=False,
            xaxis_title="Hours Played",
            yaxis_title=None,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_top10, use_container_width=True)
        
        # 4. Quick facts about distribution
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Average Time per Item", 
                f"{(total_hours/total_items):.1f} hours",
                f"Across all {analysis_type.lower()}"
            )
        with col2:
            median_hours = grouped_df['Hours'].median()
            st.metric(
                "Median Time per Item",
                f"{median_hours:.1f} hours",
                f"Half are above, half below"
            )
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")