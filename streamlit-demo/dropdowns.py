import streamlit as st
from api import fetch_data

def get_state_dropdown():
  resort_results = fetch_data("get_resorts_id")
  states = sorted(set([resort['state'] for resort in resort_results]))

  st.selectbox("Select a state", options=states, format_func=lambda x: x.title() if x else "N/A", key="selected_state")


    
