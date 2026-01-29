import streamlit as st
from v2_api import fetch_organized_resorts
from v2_resort_selector import get_location_selector, get_comparison_selector
from v2_resort_data import get_resort_data

st.markdown("""
    <style>
        .block-container {
            max-width: 1440px;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Snow Data v2", page_icon="❄️")


get_location_selector()

get_comparison_selector()

get_resort_data()