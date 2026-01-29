import streamlit as st
import json

PERSIST_KEYS = ["selected_state", "resort_search_query", "filter", 'sort']

def determine_if_should_persist(key, value):
    if key in PERSIST_KEYS:
        if isinstance(value, bool):
            return value is True
        if isinstance(value, str):
            return value != ""
        return True
    return False

def determine_if_should_load(key, value):
    if key in PERSIST_KEYS:
        return True
    return False

def read_query_params():
    if "query_params_initialized" not in st.session_state:
        params = st.query_params
        deserialized_params = json.loads(params.get('state', '{}'))
        # Only load boolean params that are True, as by default they are False in this app
        cleared_params = {k: v for k, v in deserialized_params.items() if determine_if_should_load(k, v)}
        st.session_state.update(cleared_params)
        st.session_state.query_params_initialized = True


def set_query_params():
    if "query_params_initialized" in st.session_state:
        params_to_set = {k: v for k, v in st.session_state.items() if k in PERSIST_KEYS and (isinstance(v, bool) and v is not False) or (not isinstance(v, bool))}
        st.query_params.state = json.dumps(params_to_set)