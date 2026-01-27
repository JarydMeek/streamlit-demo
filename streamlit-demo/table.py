import streamlit as st
from api import fetch_data
from cards import display_resort_card

def get_resort_table():
  resort_results = fetch_data("get_resorts_id");
  if 'selected_state' in st.session_state:
      st.write(f"You selected: {st.session_state.selected_state.title() if st.session_state.selected_state else 'N/A'}")
      filtered_resorts = [resort for resort in resort_results if resort['state'] == st.session_state.selected_state]
      for resort in filtered_resorts:
          display_resort_card(resort['id'])