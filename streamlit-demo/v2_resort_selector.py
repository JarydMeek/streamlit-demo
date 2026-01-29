import streamlit as st
from v2_api import fetch_organized_resorts
from v2_components import selectbox_with_query_params
from v2_constants import (
    COUNTRY_SELECTOR_STATE_KEY, STATE_SELECTOR_STATE_KEY, RESORT_SELECTOR_STATE_KEY,
    COMPARE_COUNTRY_SELECTOR_STATE_KEY, COMPARE_STATE_SELECTOR_STATE_KEY, COMPARE_RESORT_SELECTOR_STATE_KEY,
    COMPARE_SEASONS_STATE_KEY
)



def get_country_selector():
    organized_resorts = fetch_organized_resorts()
    countries = sorted(organized_resorts.keys())

    selectbox_with_query_params(
        "Select a country",
        options=countries,
        state_key=COUNTRY_SELECTOR_STATE_KEY,
    )


def get_state_selector():
    organized_resorts = fetch_organized_resorts()
    selected_country = st.session_state.get(COUNTRY_SELECTOR_STATE_KEY, None)

    if not selected_country or selected_country not in organized_resorts:
        # Nothing when country not selected
        return

    states = sorted(organized_resorts[selected_country].keys())

    selectbox_with_query_params(
        "Select a state",
        options=states,
        state_key=STATE_SELECTOR_STATE_KEY,
    )


def get_resort_selector():
    organized_resorts = fetch_organized_resorts()
    selected_country = st.session_state.get(COUNTRY_SELECTOR_STATE_KEY, None)

    if not selected_country or selected_country not in organized_resorts:
        # Nothing when country not selected
        return
    
    selected_state = st.session_state.get(STATE_SELECTOR_STATE_KEY, None)
    if not selected_state or selected_state not in organized_resorts[selected_country]:
        # Nothing when state not selected
        return
    
    resorts = organized_resorts[selected_country][selected_state]
    resort_names = sorted([resort["name"] for resort in resorts if "name" in resort and resort["name"] != ""])

    selectbox_with_query_params(
        "Select a resort",
        options=resort_names,
        state_key=RESORT_SELECTOR_STATE_KEY,
    )

  
def get_location_selector():
    col1, col2, col3 = st.columns([1,1,2], vertical_alignment="bottom")
    with col1:
        get_country_selector()
    with col2:
        get_state_selector()
    with col3:
        get_resort_selector()


def get_compare_country_selector():
    organized_resorts = fetch_organized_resorts()
    countries = ["None"] + sorted(organized_resorts.keys())

    selectbox_with_query_params(
        "Compare with country",
        options=countries,
        state_key=COMPARE_COUNTRY_SELECTOR_STATE_KEY,
    )


def get_compare_state_selector():
    organized_resorts = fetch_organized_resorts()
    selected_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)

    if not selected_country or selected_country == "None" or selected_country not in organized_resorts:
        return

    states = sorted(organized_resorts[selected_country].keys())

    selectbox_with_query_params(
        "Compare with state",
        options=states,
        state_key=COMPARE_STATE_SELECTOR_STATE_KEY,
    )


def get_compare_resort_selector():
    organized_resorts = fetch_organized_resorts()
    selected_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)

    if not selected_country or selected_country == "None" or selected_country not in organized_resorts:
        return

    selected_state = st.session_state.get(COMPARE_STATE_SELECTOR_STATE_KEY, None)
    if not selected_state or selected_state not in organized_resorts[selected_country]:
        return

    resorts = organized_resorts[selected_country][selected_state]
    resort_names = sorted([resort["name"] for resort in resorts if "name" in resort and resort["name"] != ""])

    selectbox_with_query_params(
        "Compare with resort",
        options=resort_names,
        state_key=COMPARE_RESORT_SELECTOR_STATE_KEY,
    )


def clear_comparison_callback():
    
    # Delete from session state - don't set, just delete
    if COMPARE_COUNTRY_SELECTOR_STATE_KEY in st.session_state:
        del st.session_state[COMPARE_COUNTRY_SELECTOR_STATE_KEY]
    if COMPARE_STATE_SELECTOR_STATE_KEY in st.session_state:
        del st.session_state[COMPARE_STATE_SELECTOR_STATE_KEY]
    if COMPARE_RESORT_SELECTOR_STATE_KEY in st.session_state:
        del st.session_state[COMPARE_RESORT_SELECTOR_STATE_KEY]
    # Clear query params
    st.query_params.pop(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
    st.query_params.pop(COMPARE_STATE_SELECTOR_STATE_KEY, None)
    st.query_params.pop(COMPARE_RESORT_SELECTOR_STATE_KEY, None)


def clear_season_comparison():
    
    st.session_state[COMPARE_SEASONS_STATE_KEY] = False
    st.query_params.pop(COMPARE_SEASONS_STATE_KEY, None)


def _is_comparing_seasons():
    
    query_params = st.query_params
    compare_seasons = st.session_state.get(COMPARE_SEASONS_STATE_KEY, False)
    if not compare_seasons and COMPARE_SEASONS_STATE_KEY in query_params:
        compare_seasons = query_params[COMPARE_SEASONS_STATE_KEY].lower() == "true"
    return compare_seasons


def _is_comparing_resorts():
    
    query_params = st.query_params
    compare_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
    if not compare_country and COMPARE_COUNTRY_SELECTOR_STATE_KEY in query_params:
        compare_country = query_params[COMPARE_COUNTRY_SELECTOR_STATE_KEY].title()
    compare_resort = st.session_state.get(COMPARE_RESORT_SELECTOR_STATE_KEY, None)
    if not compare_resort and COMPARE_RESORT_SELECTOR_STATE_KEY in query_params:
        compare_resort = query_params[COMPARE_RESORT_SELECTOR_STATE_KEY].title()
    return bool(compare_country and compare_country != "None" and compare_resort)


def get_comparison_selector():
    
    query_params = st.query_params

    # Check current state for both comparison modes
    is_comparing_seasons = _is_comparing_seasons()
    is_comparing_resorts = _is_comparing_resorts()

    # Check for resort comparison selection (even partial)
    compare_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
    if not compare_country and COMPARE_COUNTRY_SELECTOR_STATE_KEY in query_params:
        compare_country = query_params[COMPARE_COUNTRY_SELECTOR_STATE_KEY].title()
    has_resort_comparison_started = bool(compare_country and compare_country != "None")

    # Determine which mode is active/should be expanded
    is_expanded = is_comparing_resorts or is_comparing_seasons or has_resort_comparison_started

    with st.expander("Compare", expanded=is_expanded):
        # Season comparison checkbox
        # Only disable if resort comparison started AND season comparison is not active
        # (if season is active, user should be able to uncheck it)
        should_disable_season = has_resort_comparison_started and not is_comparing_seasons

        # Initialize from query params if not already in session state
        if COMPARE_SEASONS_STATE_KEY not in st.session_state and COMPARE_SEASONS_STATE_KEY in query_params:
            st.session_state[COMPARE_SEASONS_STATE_KEY] = query_params[COMPARE_SEASONS_STATE_KEY].lower() == "true"

        def on_season_checkbox_change():
            is_checked = st.session_state[COMPARE_SEASONS_STATE_KEY]
            if is_checked:
                # When enabling season comparison, clear any resort comparison
                st.query_params.update({
                    COMPARE_SEASONS_STATE_KEY: "true"
                })
                # Clear resort comparison from query params and session state
                st.query_params.pop(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
                st.query_params.pop(COMPARE_STATE_SELECTOR_STATE_KEY, None)
                st.query_params.pop(COMPARE_RESORT_SELECTOR_STATE_KEY, None)
                if COMPARE_COUNTRY_SELECTOR_STATE_KEY in st.session_state:
                    del st.session_state[COMPARE_COUNTRY_SELECTOR_STATE_KEY]
                if COMPARE_STATE_SELECTOR_STATE_KEY in st.session_state:
                    del st.session_state[COMPARE_STATE_SELECTOR_STATE_KEY]
                if COMPARE_RESORT_SELECTOR_STATE_KEY in st.session_state:
                    del st.session_state[COMPARE_RESORT_SELECTOR_STATE_KEY]
            else:
                # When disabling, remove the param entirely (don't leave false in URL)
                st.query_params.pop(COMPARE_SEASONS_STATE_KEY, None)

        st.checkbox(
            "Compare with last season (same resort, year-over-year)",
            key=COMPARE_SEASONS_STATE_KEY,
            disabled=should_disable_season,
            help="Disabled when comparing with another resort" if should_disable_season else None,
            on_change=on_season_checkbox_change
        )

        st.divider()

        # Resort comparison section
        st.write("**Or compare with another resort:**")

        if is_comparing_seasons:
            st.caption("*Clear season comparison above to compare with another resort*")
        else:
            col1, col2, col3 = st.columns([1, 1, 2], vertical_alignment="bottom")
            with col1:
                get_compare_country_selector()
            with col2:
                get_compare_state_selector()
            with col3:
                get_compare_resort_selector()

            if has_resort_comparison_started:
                st.button("Clear resort comparison", type="secondary", on_click=clear_comparison_callback)