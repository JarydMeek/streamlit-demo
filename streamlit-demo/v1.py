import streamlit as st
from dropdowns import get_state_dropdown
from table import get_resort_table 
from inputs import get_resort_search_bar
from cards import get_overall_card
from popovers import get_popover
from query_params import read_query_params, set_query_params

st.set_page_config(page_title="Snow Report v1", page_icon="❄️")


set_query_params()
read_query_params()

st.write("##### ⚠️ I know the API data is inaccurate. Turns out finding a free snow data API is hard. Just being used for demo purposes. ⚠️")

st.write("## Snow Report:")

get_state_dropdown()


get_overall_card()

api_limit = st.session_state.get("rate_limited", False)
if st.session_state.get("rate_limited", False):
  st.error("API rate limit reached. Please try again tomorrow.")
else:
  st.write("## Resorts:")

  col1, col2  = st.columns([4, 1], vertical_alignment="bottom")
  with col1:
    get_resort_search_bar()
  with col2:
    get_popover()

  get_resort_table()

