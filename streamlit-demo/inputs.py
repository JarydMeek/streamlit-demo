import streamlit as st


def get_resort_search_bar():
    st.text_input("Search for a resort", key="resort_search_query")