# pages/page4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import show_header

def create_simple_bar(df, time_column, title, color='#3498db'):
    """Create a simplified bar chart showing total listening hours."""
    summary = df.groupby(time_column).agg({
        'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
    }).reset_index()
    
    # Rename columns
    summary.columns = [time_column, 'Hours']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary[time_column],
        y=summary['Hours'],
        text=[f"{h:.1f}h" for h in summary['Hours']],
        textposition='auto',
        marker_color=color,
        marker=dict(
            line=dict(width=0)  # Remove bar border
        ),
        hovertemplate="%{x}<br>%{y:.1f} hours<extra></extra>"  # Clean hover text
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Hours Listened",
        margin=dict(t=40, b=20, l=20, r=20),
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        bargap=0.3  # Adjust space between bars
    )
     
    return fig


def show():
    """Display temporal listening patterns."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("When Do You Listen?")
    
    df = st.session_state.df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    
    try:
        # Add time-based columns
        df['year'] = df['ts'].dt.year
        df['part_of_day'] = pd.cut(
            df['ts'].dt.hour,
            bins=[0, 6, 12, 18, 24],
            labels=['Night (12AM-6AM)', 'Morning (6AM-12PM)', 
                   'Afternoon (12PM-6PM)', 'Evening (6PM-12AM)']
        )
        df['day_of_week'] = pd.Categorical(
            df['ts'].dt.day_name(),
            categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                       'Friday', 'Saturday', 'Sunday'],
            ordered=True
        )

        # Yearly Pattern (New!)
        st.subheader("Your Listening Over the Years")
        fig_yearly = create_simple_bar(df, 'year', "How Has Your Listening Changed Over Time?", '#2ecc71')
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        # Calculate year-over-year growth
        yearly_hours = df.groupby('year').agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60),
            'master_metadata_track_name': 'count'
        }).reset_index()
        yearly_hours.columns = ['Year', 'Hours', 'Streams']
        
        if len(yearly_hours) > 1:
            latest_year = yearly_hours.iloc[-1]
            previous_year = yearly_hours.iloc[-2]
            yoy_change = ((latest_year['Hours'] - previous_year['Hours']) / previous_year['Hours'] * 100)
            
            st.markdown(f"📈 In {latest_year['Year']}, you listened to "
                       f"**{latest_year['Hours']:.0f} hours** of music "
                       f"({'up' if yoy_change > 0 else 'down'} "
                       f"**{abs(yoy_change):.1f}%** from {previous_year['Year']})")
        
        st.divider()
        
        # Daily Pattern
        st.subheader("Daily Rhythm")
        fig_daily = create_simple_bar(df, 'part_of_day', "When During the Day Do You Listen Most?")
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Add insight about peak listening time
        daily_totals = df.groupby('part_of_day')['ms_played'].sum()
        peak_time = daily_totals.idxmax()
        peak_percentage = (daily_totals.max() / daily_totals.sum() * 100)
        st.markdown(f"🎵 You listen most during **{peak_time}**, which accounts for "
                   f"**{peak_percentage:.1f}%** of your total listening time.")
        
        st.divider()
        
        # Weekly Pattern
        st.subheader("Weekly Rhythm")
        fig_weekly = create_simple_bar(df, 'day_of_week', "Which Days Do You Listen Most?", '#9b59b6')
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        # Compare weekday vs weekend
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
        weekend_comp = df.groupby('is_weekend').agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
        }).reset_index()
        
        weekday_avg = weekend_comp[~weekend_comp['is_weekend']]['ms_played'].iloc[0] / 5
        weekend_avg = weekend_comp[weekend_comp['is_weekend']]['ms_played'].iloc[0] / 2
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Weekday", f"{weekday_avg:.1f} hours")
        with col2:
            diff_pct = ((weekend_avg/weekday_avg - 1) * 100)
            st.metric("Average Weekend Day", f"{weekend_avg:.1f} hours",
                     f"{diff_pct:+.1f}% vs weekday")
        
        st.divider()
        
        # Monthly pattern
        st.subheader("Monthly Rhythm")
        df['month'] = df['ts'].dt.month_name()
        df['month'] = pd.Categorical(
            df['month'],
            categories=['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'],
            ordered=True
        )
        
        # Let's do monthly pattern for the most recent year
        latest_year = df['year'].max()
        recent_df = df[df['year'] == latest_year]
        
        fig_monthly = create_simple_bar(recent_df, 'month', 
                                      f"Monthly Listening Pattern ({latest_year})", '#e74c3c')
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Add seasonal insight
        monthly_totals = recent_df.groupby('month')['ms_played'].sum()
        if len(monthly_totals) > 0:  # Only if we have monthly data
            peak_month = monthly_totals.idxmax()
            peak_month_percentage = (monthly_totals.max() / monthly_totals.sum() * 100)
            st.markdown(f"📅 Your peak listening month in {latest_year} was **{peak_month}** with "
                       f"**{peak_month_percentage:.1f}%** of your yearly listening.")
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")