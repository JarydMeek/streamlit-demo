import requests
from dotenv import load_dotenv
import os
import json
import streamlit as st
from datetime import datetime

base_url = "https://ski-resort-conditions.p.rapidapi.com/"

load_dotenv()
api_key = os.getenv("API_KEY")

default_headers = {
    "Content-Type": "application/json",
    'x-rapidapi-host': "ski-resort-conditions.p.rapidapi.com",
    'x-rapidapi-key': api_key
}


def get_from_cache(key):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    
    cache_path = os.path.join("cache", f"{key}.json")
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            cached = json.loads(f.read())
            cached_date = datetime.fromisoformat(cached["timestamp"]).date()
            today = datetime.now().date()
            
            if cached_date == today:
                print(f"Using cached data from today", cache_path)
                st.session_state.rate_limited = False
                return cached["data"]
            else:
                # Delete stale cache
                os.remove(cache_path)
                print(f"Removed stale cache file")
    return None


def write_to_cache(key, data):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    
    cache_path = os.path.join("cache", f"{key}.json")
    
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    with open(cache_path, "w") as f:
        f.write(json.dumps(cache_entry, indent=2))


def fetch_data_from_api(url):
    full_url = base_url + url
    response = requests.get(full_url, headers=default_headers)
    
    if response.status_code == 429:
        st.session_state.rate_limited = True
        print("API rate limit reached.")
        return None
    else:
        st.session_state.rate_limited = False
    response.raise_for_status()
    return response.json()


def fetch_data(url, query_params=None):
    full_url_with_params = url
    if query_params:
        param_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        full_url_with_params += "?" + param_str
    
    cached_data = get_from_cache(full_url_with_params)
    if cached_data:
        return cached_data
    
    print("Fetching new data for request:", full_url_with_params)
    data = fetch_data_from_api(full_url_with_params)
    if data is None:
        return []
    write_to_cache(full_url_with_params, data)
    return data