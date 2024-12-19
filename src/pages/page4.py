# pages/page4.py
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

def create_stacked_bar(df, time_column, title):
    """Create a stacked bar chart showing listening hours by device type."""
    summary = df.groupby([time_column, 'device_type']).agg({
        'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
    }).reset_index()
    
    fig = px.bar(
        summary,
        x=time_column,
        y='ms_played',
        color='device_type',
        title=title,
        labels={'ms_played': 'Hours Listened', time_column: ''},
        text=summary['ms_played'].round(1).astype(str) + 'h'
    )
    
    fig.update_layout(
        showlegend=True,
        legend_title="Device Type",
        yaxis_title="Hours Listened",
        margin=dict(t=40, b=20, l=20, r=20),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        bargap=0.3,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_traces(
        textposition='auto',
        hovertemplate="%{x}<br>%{y:.1f} hours<extra></extra>"
    )
     
    return fig

def show():
    """Display temporal listening patterns."""
    show_header()
    
    if not st.session_state.data_loaded:
        st.warning("Please load your data file first!")
        return
        
    st.header("When Do You Listen?")
    
    # Get base dataframe and add device type
    df = st.session_state.df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    df['device_type'] = df['platform'].apply(categorize_platform)
    
    try:
        # Create filters in columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Year filter
            years = sorted(df['ts'].dt.year.unique())
            selected_year = st.selectbox(
                "Select Year",
                ["All Years"] + list(years)
            )
            
        with col2:
            # Device filter
            devices = sorted(df['device_type'].unique())
            selected_device = st.selectbox(
                "Filter by Device Type",
                ["All Devices"] + list(devices)
            )
            
        # Apply filters
        if selected_year != "All Years":
            df = df[df['ts'].dt.year == selected_year]
            time_period = str(selected_year)
        else:
            time_period = f"{min(years)}-{max(years)}"
            
        if selected_device != "All Devices":
            df = df[df['device_type'] == selected_device]
            
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

        # Yearly Pattern (only show if All Years selected)
        if selected_year == "All Years":
            st.subheader("Your Listening Over the Years")
            fig_yearly = create_stacked_bar(df, 'year', "How Has Your Listening Changed Over Time?")
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
        st.subheader(f"Daily Rhythm {f'({time_period})' if selected_year != 'All Years' else ''}")
        fig_daily = create_stacked_bar(df, 'part_of_day', "When During the Day Do You Listen Most?")
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Add insight about peak listening time
        daily_totals = df.groupby('part_of_day')['ms_played'].sum()
        peak_time = daily_totals.idxmax()
        peak_percentage = (daily_totals.max() / daily_totals.sum() * 100)
        
        # Add device-specific insight
        daily_device = df.groupby(['part_of_day', 'device_type'])['ms_played'].sum().reset_index()
        daily_device['hours'] = daily_device['ms_played'] / (1000 * 60 * 60)
        peak_device_combo = daily_device.loc[daily_device['hours'].idxmax()]
        
        st.markdown(f"🎵 You listen most during **{peak_time}**, which accounts for "
                   f"**{peak_percentage:.1f}%** of your total listening time. "
                   f"Your peak device usage is **{peak_device_combo['device_type']}** during "
                   f"**{peak_device_combo['part_of_day']}** "
                   f"({peak_device_combo['hours']:.1f} hours).")
        
        st.divider()
        
        # Weekly Pattern
        st.subheader(f"Weekly Rhythm {f'({time_period})' if selected_year != 'All Years' else ''}")
        fig_weekly = create_stacked_bar(df, 'day_of_week', "Which Days Do You Listen Most?")
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        # Compare weekday vs weekend
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
        weekend_comp = df.groupby(['is_weekend', 'device_type']).agg({
            'ms_played': lambda x: sum(x) / (1000 * 60 * 60)  # Convert to hours
        }).reset_index()
        
        # Calculate averages by type of day
        weekday_stats = weekend_comp[~weekend_comp['is_weekend']].copy()
        weekday_stats['ms_played'] = weekday_stats['ms_played'] / 5  # Average per weekday
        weekend_stats = weekend_comp[weekend_comp['is_weekend']].copy()
        weekend_stats['ms_played'] = weekend_stats['ms_played'] / 2  # Average per weekend day
        
        col1, col2 = st.columns(2)
        with col1:
            total_weekday = weekday_stats['ms_played'].sum()
            st.metric("Average Weekday", f"{total_weekday:.1f} hours")
            if selected_device == "All Devices":
                for _, row in weekday_stats.iterrows():
                    st.write(f"- {row['device_type']}: {row['ms_played']:.1f}h")
        with col2:
            total_weekend = weekend_stats['ms_played'].sum()
            diff_pct = ((total_weekend/total_weekday - 1) * 100)
            st.metric("Average Weekend Day", f"{total_weekend:.1f} hours",
                     f"{diff_pct:+.1f}% vs weekday")
            if selected_device == "All Devices":
                for _, row in weekend_stats.iterrows():
                    st.write(f"- {row['device_type']}: {row['ms_played']:.1f}h")
        
        # Monthly pattern - only show for specific years
        if selected_year != "All Years":
            st.divider()
            st.subheader(f"Monthly Rhythm ({time_period})")
            
            df['month'] = df['ts'].dt.month_name()
            df['month'] = pd.Categorical(
                df['month'],
                categories=['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'],
                ordered=True
            )
            
            fig_monthly = create_stacked_bar(df, 'month', f"Monthly Listening Pattern ({time_period})")
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Add seasonal insight
            monthly_totals = df.groupby('month')['ms_played'].sum()
            if len(monthly_totals) > 0:  # Only if we have monthly data
                peak_month = monthly_totals.idxmax()
                peak_month_percentage = (monthly_totals.max() / monthly_totals.sum() * 100)
                
                # Add device-specific monthly insight
                monthly_device = df.groupby(['month', 'device_type'])['ms_played'].sum().reset_index()
                monthly_device['hours'] = monthly_device['ms_played'] / (1000 * 60 * 60)
                peak_month_device = monthly_device.loc[monthly_device['hours'].idxmax()]
                
                st.markdown(f"📅 Your peak listening month was **{peak_month}** with "
                           f"**{peak_month_percentage:.1f}%** of your listening. "
                           f"Most device usage was **{peak_month_device['device_type']}** in "
                           f"**{peak_month_device['month']}** "
                           f"({peak_month_device['hours']:.1f} hours).")
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")