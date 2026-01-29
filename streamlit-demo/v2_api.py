import streamlit as st
import requests
import pandas as pd
import os
import json
from v2_constants import RESORT_SELECTOR_STATE_KEY, COL_DATE, COL_TEMP_MAX, COL_TEMP_MIN, COL_TEMP_MEAN, COL_PRECIPITATION, COL_SNOWFALL, COL_SNOW_DEPTH, COL_WIND_SPEED_MAX, COL_WIND_GUSTS_MAX, COL_PRESSURE

@st.cache_data(ttl=86400)
def fetch_resorts():
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "hardcode_data", "ski_areas.json"), "r") as f:
        resorts = json.load(f)
    return resorts

def fetch_organized_resorts():
    resorts = fetch_resorts()
    organized = {}
    for resort in resorts:
        country = resort.get("countries", "Unknown")
        countries = country.split(";") if country else ["Unknown"]
        state = resort.get("regions", "Unknown")
        states = state.split(";") if state else ["Unknown"]
        
        for curr_country in countries:
          for curr_state in states:
            if curr_country not in organized:
                organized[curr_country] = {}
            if curr_state not in organized[curr_country]:
                organized[curr_country][curr_state] = []
            organized[curr_country][curr_state].append(resort)
    return organized



@st.cache_data(ttl=3600)
def fetch_historical_weather(lat, lng, start_date, end_date):
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "snowfall_sum",
            "snow_depth_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "pressure_msl_mean"
        ],
        "temperature_unit": "fahrenheit", 
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/Denver"
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame({
        COL_DATE: pd.to_datetime(data["daily"]["time"]),
        COL_TEMP_MAX: data["daily"]["temperature_2m_max"],
        COL_TEMP_MIN: data["daily"]["temperature_2m_min"],
        COL_TEMP_MEAN: data["daily"]["temperature_2m_mean"],
        COL_PRECIPITATION: data["daily"]["precipitation_sum"],
        COL_SNOWFALL: data["daily"]["snowfall_sum"],
        COL_SNOW_DEPTH: data["daily"]["snow_depth_max"],
        COL_WIND_SPEED_MAX: data["daily"]["wind_speed_10m_max"],
        COL_WIND_GUSTS_MAX: data["daily"]["wind_gusts_10m_max"],
        COL_PRESSURE: data["daily"]["pressure_msl_mean"]
    })
    
    return df


def fetch_historical_data_for_current_resort(start_date, end_date):
    if RESORT_SELECTOR_STATE_KEY not in st.session_state:
        st.error("No resort selected.")
        return None
    
    resorts = fetch_resorts()
    selected_resort_name = st.session_state[RESORT_SELECTOR_STATE_KEY]
    selected_resort = next((resort for resort in resorts if resort.get("name") == selected_resort_name), None)
    if not selected_resort:
        st.error("Selected resort not found.")
        return None
    lat = selected_resort.get("lat", None)
    lng = selected_resort.get("lng", None)
    
    if lat is None or lng is None:
        st.error("Resort does not have valid latitude/longitude.")
        return None
    
    return fetch_historical_weather(lat, lng, start_date, end_date)