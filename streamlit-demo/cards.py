import streamlit as st
from api import fetch_data, get_data_for_yesterday
from charts import resort_snowfall_chart

def display_resort_card(resort_id):
  selected_state = st.session_state.get("selected_state", None)
  resort_data = fetch_data("get_snow_by_state", {
     "state": selected_state
  })

  resort = next((resort for resort in resort_data if resort["id"] == resort_id), None)

  yesterday_data = get_data_for_yesterday("get_snow_by_state", { "state": selected_state})

  yesterday_resort_data = yesterday_data and next((resort for resort in yesterday_data if resort["id"] == resort_id), None)

  print("YESTERDAY DATA:", yesterday_resort_data)

  with st.container():
      st.header(resort.get("resort", "Unknown Resort"))
      col1, col2, col3, col4 = st.columns(4)
      with col1:
        delta = yesterday_resort_data and float(resort.get("open_lifts", "0/0").replace('n/a', '0/0').split('/')[0]) - float(yesterday_resort_data.get("open_lifts", "0/0").replace('n/a', '0/0').split('/')[0])
        st.metric("Open Lifts", resort.get("open_lifts", "N/A", ), delta=delta)
      with col2:
        delta = yesterday_resort_data and float(resort.get("open_trails", "0/0").replace('n/a', '0/0').split('/')[0]) - float(yesterday_resort_data.get("open_trails", "0/0").replace('n/a', '0/0').split('/')[0])
        st.metric("Open Trails", resort.get("open_trails", "N/A"), delta=delta)
      with col3:
        st.metric("Base Depth", f"{resort.get('base_depth', 'N/A')} in")
      with col4:
        st.metric("New Snow", f"{resort.get('snowfall24h', 'N/A')} in")
      
      resort_snowfall_chart(resort_id)