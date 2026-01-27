import requests
from dotenv import load_dotenv
import os
import json
import streamlit as st
from datetime import datetime, timedelta

base_url = "https://ski-resort-conditions.p.rapidapi.com/"

load_dotenv()
api_key = os.getenv("API_KEY")

default_headers = {
    "Content-Type": "application/json",
    'x-rapidapi-host': "ski-resort-conditions.p.rapidapi.com",
    'x-rapidapi-key': api_key
}


def get_cache_filename(key, date):
    """Generate filename with date suffix"""
    date_str = date.strftime("%Y-%m-%d")
    return f"{key}_{date_str}.json"


def get_from_cache(key):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    
    today = datetime.now().date()
    cache_filename = get_cache_filename(key, today)
    cache_path = os.path.join("cache", cache_filename)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            cached = json.loads(f.read())
            print(f"Using cached data from {today}")
            return cached["data"]
    return None


def write_to_cache(key, data):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    
    today = datetime.now().date()
    cache_filename = get_cache_filename(key, today)
    cache_path = os.path.join("cache", cache_filename)
    
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    with open(cache_path, "w") as f:
        f.write(json.dumps(cache_entry, indent=2))
    
    # Clean up files older than 30 days
    cleanup_old_cache(key)


def cleanup_old_cache(key):
    """Remove cache files older than 30 days for this key"""
    if not os.path.exists("cache"):
        return
    
    cutoff_date = datetime.now().date() - timedelta(days=30)
    
    for filename in os.listdir("cache"):
        if filename.startswith(key + "_") and filename.endswith(".json"):
            filepath = os.path.join("cache", filename)
            try:
                # Extract date from filename
                date_str = filename.replace(key + "_", "").replace(".json", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                if file_date < cutoff_date:
                    os.remove(filepath)
                    print(f"Removed old cache file: {filename}")
            except (ValueError, OSError):
                continue


def get_historical_data(url, query_params=None, days=30):
    """Fetch all cached data for the last N days"""
    full_url_with_params = url
    if query_params:
        param_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        full_url_with_params += "?" + param_str
    
    if not os.path.exists("cache"):
        return []
    
    historical_data = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)
    
    current_date = start_date
    while current_date <= end_date:
        cache_filename = get_cache_filename(full_url_with_params, current_date)
        cache_path = os.path.join("cache", cache_filename)
        
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                cached = json.loads(f.read())
                historical_data.append({
                    "date": current_date.isoformat(),
                    "data": cached["data"]
                })
        
        current_date += timedelta(days=1)
    
    return historical_data

def get_historical_data_for_resort(resort_id, days=30):
    all_data = get_historical_data('get_snow_by_state', {"state": st.session_state.get("selected_state", "")}, days=days)
    resort_historical_data = []
    
    for entry in all_data:
        date = entry["date"]
        data_for_resort = next((item for item in entry["data"] if item["id"] == resort_id), None)
        if data_for_resort:
            resort_historical_data.append({
                "date": date,
                "data": data_for_resort
            })
    
    return resort_historical_data

def get_data_for_yesterday(url, query_params=None):
    """Fetch cached data for yesterday"""
    full_url_with_params = url
    if query_params:
        param_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        full_url_with_params += "?" + param_str
    
    yesterday = datetime.now().date() - timedelta(days=1)
    cache_filename = get_cache_filename(full_url_with_params, yesterday)
    cache_path = os.path.join("cache", cache_filename)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            cached = json.loads(f.read())
            print(f"Using cached data from {yesterday}")
            return cached["data"]
    return None

def fetch_data_from_api(url):
    full_url = base_url + url
    response = requests.get(full_url, headers=default_headers)
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
    write_to_cache(full_url_with_params, data)
    return data


