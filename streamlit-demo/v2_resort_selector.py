import streamlit as st
from v2_api import fetch_organized_resorts
from v2_components import selectbox_with_query_params
from v2_constants import (
    COUNTRY_SELECTOR_STATE_KEY, STATE_SELECTOR_STATE_KEY, RESORT_SELECTOR_STATE_KEY,
    COMPARE_COUNTRY_SELECTOR_STATE_KEY, COMPARE_STATE_SELECTOR_STATE_KEY, COMPARE_RESORT_SELECTOR_STATE_KEY
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


def clear_comparison():
    """Clear the comparison resort selection."""
    st.session_state[COMPARE_COUNTRY_SELECTOR_STATE_KEY] = "None"
    if COMPARE_STATE_SELECTOR_STATE_KEY in st.session_state:
        del st.session_state[COMPARE_STATE_SELECTOR_STATE_KEY]
    if COMPARE_RESORT_SELECTOR_STATE_KEY in st.session_state:
        del st.session_state[COMPARE_RESORT_SELECTOR_STATE_KEY]
    # Clear query params
    st.query_params.pop(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
    st.query_params.pop(COMPARE_STATE_SELECTOR_STATE_KEY, None)
    st.query_params.pop(COMPARE_RESORT_SELECTOR_STATE_KEY, None)


def get_comparison_selector():
    """Optional comparison resort selector."""
    # Check both session state and query params to determine comparison state
    query_params = st.query_params

    compare_country = st.session_state.get(COMPARE_COUNTRY_SELECTOR_STATE_KEY, None)
    if not compare_country and COMPARE_COUNTRY_SELECTOR_STATE_KEY in query_params:
        compare_country = query_params[COMPARE_COUNTRY_SELECTOR_STATE_KEY].title()

    compare_resort = st.session_state.get(COMPARE_RESORT_SELECTOR_STATE_KEY, None)
    if not compare_resort and COMPARE_RESORT_SELECTOR_STATE_KEY in query_params:
        compare_resort = query_params[COMPARE_RESORT_SELECTOR_STATE_KEY].title()

    has_comparison_selection = bool(compare_country and compare_country != "None")
    is_fully_comparing = has_comparison_selection and bool(compare_resort)

    with st.expander("Compare with another resort", expanded=is_fully_comparing):
        col1, col2, col3 = st.columns([1, 1, 2], vertical_alignment="bottom")
        with col1:
            get_compare_country_selector()
        with col2:
            get_compare_state_selector()
        with col3:
            get_compare_resort_selector()

        if has_comparison_selection:
            if st.button("Clear comparison", type="secondary"):
                clear_comparison()
                st.rerun()