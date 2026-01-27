import streamlit as st
from dropdowns import get_state_dropdown
from table import get_resort_table 
from inputs import get_resort_search_bar
from cards import get_overall_card

st.write("##### ⚠️ I know the API data is inaccurate. Turns out finding a free snow data API is hard. Just being used for demo purposes. ⚠️")

st.write("## Snow Report:")

get_state_dropdown()

get_overall_card()

st.write("## Resorts:")

get_resort_search_bar()

get_resort_table()