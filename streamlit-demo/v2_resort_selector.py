import streamlit as st
from v2_api import fetch_organized_resorts
from v2_components import selectbox_with_query_params
from v2_constants import COUNTRY_SELECTOR_STATE_KEY, STATE_SELECTOR_STATE_KEY, RESORT_SELECTOR_STATE_KEY



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