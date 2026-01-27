import streamlit as st
from api import get_historical_data_for_resort
import pandas as pd

  
def resort_snowfall_chart(resort_id):
    historical_data = get_historical_data_for_resort(resort_id, days=30)
    if not historical_data:
        st.write("No historical data available.")
        return

    dates = [entry["date"] for entry in historical_data]
    snowfall_24h = [float(entry["data"].get("snowfall24h", "0").replace('\"', '')) for entry in historical_data]

    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Snowfall (24h)": snowfall_24h
    })
    st.write("Snowfall in the Last 30 Days")
    st.bar_chart(df.set_index("Date"), height=200)