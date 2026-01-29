import streamlit as st
from datetime import date, timedelta

def selectbox_with_query_params(label, options, state_key):
    query_param_value = None
    query_params = st.query_params
    if state_key in query_params:
        query_param_value = query_params[state_key].title()

    index = 0
    if query_param_value and query_param_value in options:
        index = options.index(query_param_value)

    st.selectbox(
        label,
        options=options,
        format_func=lambda x: x.title() if x else "N/A",
        key=state_key,
        index=index,
        on_change=lambda: st.query_params.update({state_key: st.session_state[state_key].lower()}),
    )


def date_range_with_query_params(label, state_key, min_value=None, max_value=None):
    query_param_value = None
    query_params = st.query_params
    if state_key in query_params:
        query_param_value = query_params[state_key]

    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    if query_param_value:
        try:
            start_str, end_str = query_param_value.split("_to_")
            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str)
        except Exception:
            pass

    # Initialize session state if it doesn't exist
    if state_key not in st.session_state:
        st.session_state[state_key] = (start_date, end_date)
        # Sync query params with initial session state
        st.query_params.update({state_key: f"{start_date.isoformat()}_to_{end_date.isoformat()}"})

    # Quick selector buttons
    cols = st.columns([3, 1, 1], vertical_alignment="bottom")
    
    with cols[1]:
        if st.button("This Season", key=f"{state_key}_this_season"):
            today = date.today()
            current_year = today.year
            current_month = today.month
            
            # Figure out which season year we're in
            if current_month >= 10:  # Oct-Dec
                season_start_year = current_year
            elif current_month <= 4:  # Jan-Apr
                season_start_year = current_year - 1
            else:  # May-Sep (off-season)
                season_start_year = current_year - 1
            
            # This Season: Oct 1 to either today (if in season) or Apr 30 (if season ended)
            start_date = date(season_start_year, 10, 1)
            if current_month >= 5 and current_month <= 9:
                # Off-season: show completed season
                end_date = date(season_start_year + 1, 4, 30)
            else:
                # In season: show up to today
                end_date = today
            
            st.session_state[state_key] = (start_date, end_date)
            st.query_params.update({state_key: f"{start_date.isoformat()}_to_{end_date.isoformat()}"})
            st.rerun()
    
    with cols[2]:
        if st.button("Last Season", key=f"{state_key}_last_season"):
            today = date.today()
            current_year = today.year
            current_month = today.month
            
            # Figure out which season year we're in
            if current_month >= 10:  # Oct-Dec
                season_start_year = current_year
            elif current_month <= 4:  # Jan-Apr
                season_start_year = current_year - 1
            else:  # May-Sep (off-season)
                season_start_year = current_year - 1
            
            # Last Season: full season from previous year
            start_date = date(season_start_year - 1, 10, 1)
            end_date = date(season_start_year, 4, 30)
            
            st.session_state[state_key] = (start_date, end_date)
            st.query_params.update({state_key: f"{start_date.isoformat()}_to_{end_date.isoformat()}"})
            st.rerun()

    with cols[0]:
      selected_date_range = st.date_input(
          label,
          min_value=min_value,
          max_value=max_value,
          key=state_key,
          on_change=lambda: st.query_params.update({state_key: f"{st.session_state[state_key][0].isoformat()}_to_{st.session_state[state_key][1].isoformat()}"}),
      )

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start, end = selected_date_range
        if (end - start).days > 365:
            end = start + timedelta(days=365)
            selected_date_range = (start, end)
            st.warning("Date range was capped to 1 year from the start date.")

    return selected_date_range