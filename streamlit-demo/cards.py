import streamlit as st
from api import fetch_data
from utils import get_score_metric

def display_resort_card(resort_id):
  selected_state = st.session_state.get("selected_state", None)
  resort_data = fetch_data("get_snow_by_state", {
     "state": selected_state
  })

  resort = next((resort for resort in resort_data if resort["id"] == resort_id), None)

  with st.container(border=True):
      col1a, col2a = st.columns([3, 1])
      with col1a:
        st.header(resort.get("resort", "Unknown Resort"))
      with col2a:
        open_trails = float(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[0])
        total_trails = float(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[1])
        open_trails_percent = (open_trails / total_trails * 100) if total_trails > 0 else 0
        open_lifts = float(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[0])
        total_lifts = float(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[1])
        open_lifts_percent = (open_lifts / total_lifts * 100) if total_lifts > 0 else 0
        overall_score = (open_trails_percent + open_lifts_percent) / 2
        get_score_metric(overall_score, "Overall")

      col1, col2, col3, col4 = st.columns(4)
      with col1:
        st.metric("Open Lifts", resort.get("open_lifts", "N/A", ))
      with col2:
        st.metric("Open Trails", resort.get("open_trails", "N/A"))
      with col3:
        st.metric("Base Depth", f"{resort.get('base_depth', 'N/A')}")
      with col4:
        st.metric("New Snow", f"{resort.get('snowfall24h', 'N/A')}")


def get_overall_card():
  resort_data = fetch_data("get_snow_by_state", {
     "state": st.session_state.get("selected_state", None)
  })

  total_open_lifts = sum(int(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[0]) for resort in resort_data)
  total_lifts = sum(int(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[1]) for resort in resort_data)
  total_lift_percent = (total_open_lifts / total_lifts * 100) if total_lifts > 0 else 0

  total_open_trails = sum(int(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[0]) for resort in resort_data)
  total_trails = sum(int(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[1]) for resort in resort_data)
  total_trail_percent = (total_open_trails / total_trails * 100) if total_trails > 0 else 0

  with st.container(border=True):
      col1a, col2a, col3a = st.columns([3, 1, 1])
      with col1a:
        st.header(f"Overall {st.session_state.get('selected_state', 'All').title()} Stats")
      with col2a:
        st.metric("Number of Resorts", len(resort_data))
      with col3a:
        overall_score = (total_lift_percent + total_trail_percent) / 2
        get_score_metric(overall_score, "Overall")
      col1, col2 = st.columns(2)
      with col1:
        st.metric("Total Open Lifts", f"{total_open_lifts}/{total_lifts}")
        st.progress(total_lift_percent / 100.0, text=f"Lift Availability: {total_lift_percent:.1f}%")
      with col2:
        st.metric("Total Open Trails", f"{total_open_trails}/{total_trails}")
        st.progress(total_trail_percent / 100.0, text=f"Trail Availability: {total_trail_percent:.1f}%")
      