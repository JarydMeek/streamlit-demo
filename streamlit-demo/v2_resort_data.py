import streamlit as st
from v2_api import (
    fetch_historical_data_for_current_resort, fetch_historical_data_for_comparison_resort,
    fetch_this_season_data_for_current_resort, fetch_last_season_data_for_current_resort,
    get_season_dates
)
from v2_components import date_range_with_query_params
from v2_constants import (
    COL_PRECIPITATION, COL_PRESSURE, COL_SNOWFALL, RESORT_SELECTOR_STATE_KEY,
    DATE_RANGE_STATE_KEY, STATE_SELECTOR_STATE_KEY, COL_DATE, COL_TEMP_MAX,
    COL_TEMP_MIN, COL_TEMP_MEAN, COL_WIND_SPEED_MAX, COL_WIND_GUSTS_MAX,
    COMPARE_RESORT_SELECTOR_STATE_KEY, COMPARE_STATE_SELECTOR_STATE_KEY,
    COMPARE_COUNTRY_SELECTOR_STATE_KEY, COMPARE_SEASONS_STATE_KEY
)
from v2_utils import format_date
import plotly.graph_objects as go
import pandas as pd

# Column for day of season (used in season comparisons)
COL_DAY_OF_SEASON = "Day of Season"

# Colors for primary and comparison resorts
PRIMARY_COLOR = '#1f77b4'
PRIMARY_COLOR_ALT = '#2ca02c'
PRIMARY_COLOR_THIRD = '#d62728'
COMPARE_COLOR = '#ff7f0e'
COMPARE_COLOR_ALT = '#9467bd'
COMPARE_COLOR_THIRD = '#e377c2'

def get_resort_data():
    selected_resort = st.session_state.get(RESORT_SELECTOR_STATE_KEY, "N/A")
    selected_state = st.session_state.get(STATE_SELECTOR_STATE_KEY, "N/A")

    # Check if season comparison is enabled
    compare_seasons = st.session_state.get(COMPARE_SEASONS_STATE_KEY, False)

    if compare_seasons:
        # Season comparison mode
        get_season_comparison_data(selected_resort, selected_state)
    else:
        # Normal mode with optional resort comparison
        get_normal_resort_data(selected_resort, selected_state)


def get_season_comparison_data(selected_resort, selected_state):
    season_dates = get_season_dates()

    this_season_data = fetch_this_season_data_for_current_resort()
    last_season_data = fetch_last_season_data_for_current_resort()

    if this_season_data is None:
        st.error("Error fetching this season's data.")
        return

    if last_season_data is None:
        st.error("Error fetching last season's data.")
        return

    # Add day-of-season column for alignment
    this_season_start = season_dates['this_season_start']
    last_season_start = season_dates['last_season_start']

    this_season_data = this_season_data.copy()
    last_season_data = last_season_data.copy()

    this_season_data[COL_DAY_OF_SEASON] = (this_season_data[COL_DATE] - pd.Timestamp(this_season_start)).dt.days
    last_season_data[COL_DAY_OF_SEASON] = (last_season_data[COL_DATE] - pd.Timestamp(last_season_start)).dt.days

    # Get season year labels
    this_season_label = f"{this_season_start.year}-{this_season_start.year + 1}"
    last_season_label = f"{last_season_start.year}-{last_season_start.year + 1}"

    # Display header
    st.write(f"### {selected_resort}: This Season vs Last Season")
    st.write(f"##### {this_season_label} vs {last_season_label}")
    st.caption(f"🔵 This Season ({this_season_label}) | 🟠 Last Season ({last_season_label})")
    st.caption(f"This season: {format_date(season_dates['this_season_start'])} to {format_date(season_dates['this_season_end'])} ({season_dates['days_into_season']} days)")

    # Use day of season for x-axis
    get_season_temps(this_season_data, last_season_data, this_season_label, last_season_label)

    col1a, col2a = st.columns(2)
    with col1a:
        get_season_snowfall(this_season_data, last_season_data, this_season_label, last_season_label)
    with col2a:
        get_season_pressure(this_season_data, last_season_data, this_season_label, last_season_label)

    col1b, col2b = st.columns(2)
    with col1b:
        get_season_wind(this_season_data, last_season_data, this_season_label, last_season_label)
    with col2b:
        get_season_cumulative_snowfall(this_season_data, last_season_data, this_season_label, last_season_label, season_dates)


def get_normal_resort_data(selected_resort, selected_state):
    date_range = date_range_with_query_params(
        "Select date range for historical weather data",
        state_key=DATE_RANGE_STATE_KEY)

    data = fetch_historical_data_for_current_resort(
        start_date=date_range[0],
        end_date=date_range[1],
    )

    # Fetch comparison data if a comparison resort is selected
    compare_data = fetch_historical_data_for_comparison_resort(
        start_date=date_range[0],
        end_date=date_range[1],
    )
    compare_resort = st.session_state.get(COMPARE_RESORT_SELECTOR_STATE_KEY, None)
    compare_state = st.session_state.get(COMPARE_STATE_SELECTOR_STATE_KEY, None)
    compare_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)

    # Check if comparison is valid
    has_comparison = (
        compare_data is not None and
        compare_country and compare_country != "None" and
        compare_resort
    )

    if data is None:
        st.error("Error fetching historical data for the selected resort and date range.")
        return

    # Display header
    if has_comparison:
        st.write(f"### {selected_resort} vs {compare_resort}")
        st.write(f"##### {format_date(date_range[0])} to {format_date(date_range[1])}")
        st.caption(f"🔵 {selected_resort}, {selected_state} | 🟠 {compare_resort}, {compare_state}")
    else:
        st.write(f"### {selected_resort}, {selected_state}")
        st.write(f"##### {format_date(date_range[0])} to {format_date(date_range[1])}")

    # Detect storms for highlighting
    storm_periods = detect_storm_periods(data)

    get_resort_temps(data, compare_data if has_comparison else None, selected_resort, compare_resort)

    col1a, col2a = st.columns(2)
    with col1a:
        get_resort_snowfall(data, storm_periods, compare_data if has_comparison else None, selected_resort, compare_resort)
    with col2a:
        get_resort_pressure(data, compare_data if has_comparison else None, selected_resort, compare_resort)

    col1b, col2b = st.columns(2)
    with col1b:
        get_resort_wind(data, compare_data if has_comparison else None, selected_resort, compare_resort)
    with col2b:
        get_resort_cumulative_snowfall(data, compare_data if has_comparison else None, selected_resort, compare_resort)

    # Combined metrics - only show when not comparing resorts
    if not has_comparison:
        st.write("### Combined Metrics for Deeper Insights")
        st.write("These combined charts help visualize relationships between different weather parameters. **I highly recommend setting the date range to no more than a few months for optimal clarity.**")
        get_resort_snowfall_vs_pressure(data)
        get_custom_comparison(data)


def detect_storm_periods(data, threshold=0.5):
    if data is None or data.empty:
        return []
    
    # Mark days as "storm days" if snowfall or precip exceeds threshold
    data['is_storm'] = (data[COL_SNOWFALL] >= threshold) | (data[COL_PRECIPITATION] >= threshold)
    
    storm_periods = []
    in_storm = False
    start_date = None
    total_snow = 0
    
    for idx, row in data.iterrows():
        if row['is_storm'] and not in_storm:
            # Start of new storm
            in_storm = True
            start_date = row[COL_DATE]
            total_snow = row[COL_SNOWFALL]
        elif row['is_storm'] and in_storm:
            # Continuing storm
            total_snow += row[COL_SNOWFALL]
        elif not row['is_storm'] and in_storm:
            # End of storm
            end_date = data.iloc[idx - 1][COL_DATE]
            storm_periods.append((start_date, end_date, total_snow))
            in_storm = False
            total_snow = 0
    
    # Handle case where storm period extends to end of data
    if in_storm:
        end_date = data.iloc[-1][COL_DATE]
        storm_periods.append((start_date, end_date, total_snow))
    
    return storm_periods


def get_resort_temps(data, compare_data=None, primary_name="Primary", compare_name="Compare"):
    if data is None or data.empty:
        st.error("No data available to display temperatures.")
        return

    st.write("###### Daily Temperatures")

    fig = go.Figure()

    # Primary resort data
    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_TEMP_MAX],
        name=f"Max ({primary_name})" if compare_data is not None else "Max",
        line=dict(color=PRIMARY_COLOR),
        legendgroup="primary"
    ))

    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_TEMP_MEAN],
        name=f"Mean ({primary_name})" if compare_data is not None else "Mean",
        line=dict(color=PRIMARY_COLOR_ALT),
        legendgroup="primary"
    ))

    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_TEMP_MIN],
        name=f"Min ({primary_name})" if compare_data is not None else "Min",
        line=dict(color=PRIMARY_COLOR_THIRD),
        legendgroup="primary"
    ))

    # Comparison resort data
    if compare_data is not None and not compare_data.empty:
        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_TEMP_MAX],
            name=f"Max ({compare_name})",
            line=dict(color=COMPARE_COLOR, dash='dash'),
            legendgroup="compare"
        ))

        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_TEMP_MEAN],
            name=f"Mean ({compare_name})",
            line=dict(color=COMPARE_COLOR_ALT, dash='dash'),
            legendgroup="compare"
        ))

        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_TEMP_MIN],
            name=f"Min ({compare_name})",
            line=dict(color=COMPARE_COLOR_THIRD, dash='dash'),
            legendgroup="compare"
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Temperature (°F)",
        height=250 if compare_data is None else 300,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_resort_snowfall(data, storm_periods=None, compare_data=None, primary_name="Primary", compare_name="Compare"):
    if data is None or data.empty:
        st.error("No data available to display snowfall.")
        return

    st.write("###### Daily Snowfall")

    # Show storm summary if storms detected
    if storm_periods and len(storm_periods) > 0:
        multi_day_storms = [s for s in storm_periods if s[0] != s[1]]
        if multi_day_storms:
            st.caption(f"🌨️ {len(multi_day_storms)} multi-day storm(s) detected")

    fig = go.Figure()

    # Primary resort data
    fig.add_trace(go.Bar(
        x=data[COL_DATE],
        y=data[COL_SNOWFALL],
        name=primary_name if compare_data is not None else "Snowfall",
        marker_color=PRIMARY_COLOR,
        opacity=0.7 if compare_data is not None else 1.0
    ))

    # Comparison resort data
    if compare_data is not None and not compare_data.empty:
        fig.add_trace(go.Bar(
            x=compare_data[COL_DATE],
            y=compare_data[COL_SNOWFALL],
            name=compare_name,
            marker_color=COMPARE_COLOR,
            opacity=0.7
        ))

    # Add storm period shading
    if storm_periods:
        for start, end, total in storm_periods:
            if start != end:  # Only shade multi-day storms
                fig.add_vrect(
                    x0=start, x1=end,
                    fillcolor="rgba(255, 200, 100, 0.2)",
                    layer="below",
                    line_width=0,
                )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Snowfall (in)",
        height=250,
        showlegend=compare_data is not None,
        margin=dict(t=20, b=40, l=40, r=40),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_resort_wind(data, compare_data=None, primary_name="Primary", compare_name="Compare"):
    if data is None or data.empty:
        st.error("No data available to display wind data.")
        return

    st.write("###### Daily Wind")

    fig = go.Figure()

    # Primary resort data
    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_WIND_GUSTS_MAX],
        name=f"Max Gusts ({primary_name})" if compare_data is not None else "Max Gusts",
        line=dict(color="rgba(128, 128, 128, 0.5)"),
        legendgroup="primary"
    ))

    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_WIND_SPEED_MAX],
        name=f"Max Wind ({primary_name})" if compare_data is not None else "Max Wind Speed",
        line=dict(color=PRIMARY_COLOR),
        legendgroup="primary"
    ))

    # Comparison resort data
    if compare_data is not None and not compare_data.empty:
        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_WIND_GUSTS_MAX],
            name=f"Max Gusts ({compare_name})",
            line=dict(color="rgba(200, 150, 100, 0.5)", dash='dash'),
            legendgroup="compare"
        ))

        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_WIND_SPEED_MAX],
            name=f"Max Wind ({compare_name})",
            line=dict(color=COMPARE_COLOR, dash='dash'),
            legendgroup="compare"
        ))

    # Add reference line for high wind (lifts close at ~30 mph)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(255, 0, 0, 0.5)",
                  annotation_text="High Wind", annotation_position="right")

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Wind Speed (mph)",
        height=250 if compare_data is None else 300,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_resort_cumulative_snowfall(data, compare_data=None, primary_name="Primary", compare_name="Compare"):
    if data is None or data.empty:
        st.error("No data available to display cumulative snowfall.")
        return

    st.write("###### Cumulative Snowfall")

    # Calculate cumulative sum for primary
    cumulative_snow = data[COL_SNOWFALL].cumsum()
    total_snow = cumulative_snow.iloc[-1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=cumulative_snow,
        name=primary_name if compare_data is not None else "Cumulative Snowfall",
        line=dict(color=PRIMARY_COLOR_ALT),
        fill='tozeroy' if compare_data is None else None
    ))

    # Comparison resort data
    compare_total = None
    if compare_data is not None and not compare_data.empty:
        compare_cumulative = compare_data[COL_SNOWFALL].cumsum()
        compare_total = compare_cumulative.iloc[-1]

        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_cumulative,
            name=compare_name,
            line=dict(color=COMPARE_COLOR, dash='dash')
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Snowfall (in)",
        height=250,
        showlegend=compare_data is not None,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)

    if compare_data is not None and compare_total is not None:
        st.caption(f"Total: {primary_name}: {total_snow:.1f}\" | {compare_name}: {compare_total:.1f}\"")
    else:
        st.caption(f"Total snowfall: {total_snow:.1f} inches")


def get_resort_pressure(data, compare_data=None, primary_name="Primary", compare_name="Compare"):
    if data is None or data.empty:
        st.error("No data available to display pressure.")
        return

    st.write("###### Daily Pressure")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_PRESSURE],
        mode='lines',
        name=primary_name if compare_data is not None else 'Pressure',
        line=dict(color=PRIMARY_COLOR)
    ))

    # Comparison resort data
    if compare_data is not None and not compare_data.empty:
        fig.add_trace(go.Scatter(
            x=compare_data[COL_DATE],
            y=compare_data[COL_PRESSURE],
            mode='lines',
            name=compare_name,
            line=dict(color=COMPARE_COLOR, dash='dash')
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Pressure (mb)",
        height=250,
        yaxis=dict(
            rangemode='normal'
        ),
        showlegend=compare_data is not None,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)

def get_resort_snowfall_vs_pressure(data):
    if data is None or data.empty:
        st.error("No data available to display snowfall vs pressure.")
        return

    st.write("###### Daily Snowfall vs Pressure")
    st.write("This chart shows daily snowfall (bars) against atmospheric pressure (line). Generally, lower pressure is associated with stormy weather and higher snowfall.")

    fig = go.Figure()

    # Calculate average pressure for the period
    avg_pressure = data[COL_PRESSURE].mean()

    # Find continuous below-average pressure periods
    data_sorted = data.sort_values(COL_DATE).reset_index(drop=True)
    low_pressure_periods = []
    in_low_period = False
    period_start = None

    for idx, row in data_sorted.iterrows():
        is_low = row[COL_PRESSURE] < avg_pressure

        if is_low and not in_low_period:
            # Start of a new low pressure period
            in_low_period = True
            period_start = row[COL_DATE]
        elif not is_low and in_low_period:
            # End of low pressure period
            period_end = data_sorted.iloc[idx - 1][COL_DATE]
            low_pressure_periods.append((period_start, period_end))
            in_low_period = False
            period_start = None

    # Handle case where low pressure extends to end of data
    if in_low_period:
        period_end = data_sorted.iloc[-1][COL_DATE]
        low_pressure_periods.append((period_start, period_end))

    # Add vertical shading for each low pressure period
    for start_date, end_date in low_pressure_periods:
        # Add half a day padding on each side for visibility
        fig.add_vrect(
            x0=start_date - pd.Timedelta(hours=12),
            x1=end_date + pd.Timedelta(hours=12),
            fillcolor="rgba(255, 150, 150, 0.3)",
            layer="below",
            line_width=0,
        )

    # Add pressure line on primary y-axis
    fig.add_trace(go.Scatter(
        x=data[COL_DATE],
        y=data[COL_PRESSURE],
        mode='lines',
        name='Pressure',
        line=dict(color='#1f77b4'),
        yaxis='y'
    ))
    
    # Add average pressure line
    fig.add_hline(
        y=avg_pressure,
        line_dash="dash",
        line_color="rgba(100, 100, 100, 0.5)",
        annotation_text=f"Avg ({avg_pressure:.0f} mb)",
        annotation_position="right"
    )
    
    # Add snowfall bars on secondary y-axis
    fig.add_trace(go.Bar(
        x=data[COL_DATE],
        y=data[COL_SNOWFALL],
        name='Snowfall',
        marker_color='#2ca02c',
        yaxis='y2'
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        height=500,
        margin=dict(t=20, b=40, l=40, r=40),
        # Primary y-axis (pressure)
        yaxis=dict(
            title="Pressure (mb)",
            rangemode='normal',
            side='left'
        ),
        # Secondary y-axis (snowfall)
        yaxis2=dict(
            title="Snowfall (in)",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig)


def get_custom_comparison(data):
    if data is None or data.empty:
        st.error("No data available for custom comparison.")
        return
    
    st.write("###### Custom Metric Comparison")
    
    # Define available metrics (excluding date)
    metrics = [
        COL_TEMP_MAX,
        COL_TEMP_MIN,
        COL_TEMP_MEAN,
        COL_SNOWFALL,
        COL_PRECIPITATION,
        COL_PRESSURE,
        COL_WIND_SPEED_MAX,
        COL_WIND_GUSTS_MAX
    ]
    
    # Bar chart metrics (rest will be lines)
    bar_metrics = [COL_SNOWFALL, COL_PRECIPITATION]
    
    col1, col2 = st.columns(2)
    with col1:
        metric1 = st.selectbox(
            "Primary Metric (Left Y-axis)",
            options=metrics,
            index=metrics.index(COL_PRESSURE)
        )
    with col2:
        metric2 = st.selectbox(
            "Secondary Metric (Right Y-axis)",
            options=metrics,
            index=metrics.index(COL_SNOWFALL)
        )
    
    fig = go.Figure()
    
    # Add first metric
    if metric1 in bar_metrics:
        fig.add_trace(go.Bar(
            x=data[COL_DATE],
            y=data[metric1],
            name=metric1,
            marker_color='#1f77b4',
            yaxis='y'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data[COL_DATE],
            y=data[metric1],
            mode='lines',
            name=metric1,
            line=dict(color='#1f77b4'),
            yaxis='y'
        ))
    
    # Add second metric
    if metric2 in bar_metrics:
        fig.add_trace(go.Bar(
            x=data[COL_DATE],
            y=data[metric2],
            name=metric2,
            marker_color='#2ca02c',
            yaxis='y2'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data[COL_DATE],
            y=data[metric2],
            mode='lines',
            name=metric2,
            line=dict(color='#2ca02c'),
            yaxis='y2'
        ))
    
    fig.update_layout(
        xaxis_title="Date",
        height=250,
        margin=dict(t=20, b=40, l=40, r=40),
        yaxis=dict(
            title=metric1,
            rangemode='normal',
            side='left'
        ),
        yaxis2=dict(
            title=metric2,
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig)


# ============================================
# Season Comparison Charts (using day-of-season)
# ============================================

def get_season_temps(this_season_data, last_season_data, this_label, last_label):
    
    st.write("###### Daily Temperatures")

    fig = go.Figure()

    # This season (solid lines)
    fig.add_trace(go.Scatter(
        x=this_season_data[COL_DAY_OF_SEASON],
        y=this_season_data[COL_TEMP_MEAN],
        name=f"Mean ({this_label})",
        line=dict(color=PRIMARY_COLOR, shape='spline'),
        legendgroup="this"
    ))

    # Last season (dashed lines)
    fig.add_trace(go.Scatter(
        x=last_season_data[COL_DAY_OF_SEASON],
        y=last_season_data[COL_TEMP_MEAN],
        name=f"Mean ({last_label})",
        line=dict(color=COMPARE_COLOR, dash='dash', shape='spline'),
        legendgroup="last"
    ))

    fig.update_layout(
        xaxis_title="Day of Season",
        yaxis_title="Temperature (°F)",
        height=300,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_season_snowfall(this_season_data, last_season_data, this_label, last_label):
    
    st.write("###### Daily Snowfall")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=this_season_data[COL_DAY_OF_SEASON],
        y=this_season_data[COL_SNOWFALL],
        name=this_label,
        marker_color=PRIMARY_COLOR,
        opacity=0.7
    ))

    fig.add_trace(go.Bar(
        x=last_season_data[COL_DAY_OF_SEASON],
        y=last_season_data[COL_SNOWFALL],
        name=last_label,
        marker_color=COMPARE_COLOR,
        opacity=0.7
    ))

    fig.update_layout(
        xaxis_title="Day of Season",
        yaxis_title="Snowfall (in)",
        height=250,
        margin=dict(t=20, b=40, l=40, r=40),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_season_pressure(this_season_data, last_season_data, this_label, last_label):
    
    st.write("###### Daily Pressure")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=this_season_data[COL_DAY_OF_SEASON],
        y=this_season_data[COL_PRESSURE],
        mode='lines',
        name=this_label,
        line=dict(color=PRIMARY_COLOR, shape='spline')
    ))

    fig.add_trace(go.Scatter(
        x=last_season_data[COL_DAY_OF_SEASON],
        y=last_season_data[COL_PRESSURE],
        mode='lines',
        name=last_label,
        line=dict(color=COMPARE_COLOR, dash='dash', shape='spline')
    ))

    fig.update_layout(
        xaxis_title="Day of Season",
        yaxis_title="Pressure (mb)",
        height=250,
        yaxis=dict(rangemode='normal'),
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_season_wind(this_season_data, last_season_data, this_label, last_label):
    
    st.write("###### Daily Wind")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=this_season_data[COL_DAY_OF_SEASON],
        y=this_season_data[COL_WIND_SPEED_MAX],
        name=f"Max Wind ({this_label})",
        line=dict(color=PRIMARY_COLOR, shape='spline'),
        legendgroup="this"
    ))

    fig.add_trace(go.Scatter(
        x=last_season_data[COL_DAY_OF_SEASON],
        y=last_season_data[COL_WIND_SPEED_MAX],
        name=f"Max Wind ({last_label})",
        line=dict(color=COMPARE_COLOR, dash='dash', shape='spline'),
        legendgroup="last"
    ))

    fig.add_hline(y=30, line_dash="dash", line_color="rgba(255, 0, 0, 0.5)",
                  annotation_text="High Wind", annotation_position="right")

    fig.update_layout(
        xaxis_title="Day of Season",
        yaxis_title="Wind Speed (mph)",
        height=300,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def get_season_cumulative_snowfall(this_season_data, last_season_data, this_label, last_label, season_dates):
    
    st.write("###### Cumulative Snowfall")

    # Calculate cumulative sums
    this_cumulative = this_season_data[COL_SNOWFALL].cumsum()
    last_cumulative = last_season_data[COL_SNOWFALL].cumsum()

    this_total = this_cumulative.iloc[-1] if len(this_cumulative) > 0 else 0
    last_total = last_cumulative.iloc[-1] if len(last_cumulative) > 0 else 0

    # Get last season total at equivalent day (for fair comparison)
    days_into_season = season_dates['days_into_season']
    last_at_equivalent = last_cumulative.iloc[days_into_season] if len(last_cumulative) > days_into_season else last_total

    fig = go.Figure()

    # This season
    fig.add_trace(go.Scatter(
        x=this_season_data[COL_DAY_OF_SEASON],
        y=this_cumulative,
        name=this_label,
        line=dict(color=PRIMARY_COLOR_ALT)
    ))

    # Last season (full season)
    fig.add_trace(go.Scatter(
        x=last_season_data[COL_DAY_OF_SEASON],
        y=last_cumulative,
        name=last_label,
        line=dict(color=COMPARE_COLOR, dash='dash')
    ))

    # Add vertical line at current day of season
    fig.add_vline(
        x=days_into_season,
        line_dash="dot",
        line_color="rgba(100, 100, 100, 0.5)",
        annotation_text="Today",
        annotation_position="top"
    )

    fig.update_layout(
        xaxis_title="Day of Season",
        yaxis_title="Total Snowfall (in)",
        height=250,
        margin=dict(t=10, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig)

    # Show comparison with metrics
    diff = this_total - last_at_equivalent
    diff_str = f"+{diff:.1f}" if diff >= 0 else f"{diff:.1f}"

    # Calculate percentage difference
    if last_at_equivalent > 0:
        pct_diff = ((this_total - last_at_equivalent) / last_at_equivalent) * 100
        pct_str = f"+{pct_diff:.0f}%" if pct_diff >= 0 else f"{pct_diff:.0f}%"
    else:
        pct_diff = 0
        pct_str = "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Season", f"{this_total:.1f}\"", delta=f"{diff_str}\" vs last year")
    with col2:
        st.metric("Last Season (same point)", f"{last_at_equivalent:.1f}\"")
    with col3:
        st.metric("Year-over-Year", pct_str)

    st.caption(f"Last season final total: {last_total:.1f}\"")