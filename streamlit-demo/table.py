import streamlit as st
from api import fetch_data
from cards import display_resort_card
from utils import get_overall_score

def get_resort_table():
  resort_results = fetch_data("get_snow_by_state", {"state": st.session_state.selected_state})

  if 'selected_state' in st.session_state:
      filtered_resorts = [resort for resort in resort_results if resort['state'] == st.session_state.selected_state]
  
      search_query = st.session_state.get("resort_search_query", "").lower()
      searched_resorts = [resort for resort in filtered_resorts if search_query in resort['resort'].lower()]

      applied_filters_resorts = searched_resorts
    
      if 'filter' in st.session_state:
          filters = st.session_state['filter']
          # Overall score
          if 'overall_score' in filters and filters['overall_score'] != []:
              applied_filters_resorts = [resort for resort in applied_filters_resorts if get_overall_score(resort)[1] in filters['overall_score']]
          # New snow
          if 'new_snow' in filters and filters['new_snow']:
              applied_filters_resorts = [resort for resort in applied_filters_resorts if float(resort.get('snowfall24h', "0\"").replace('\"', '')) > 0]
      col1a, col2a, col3a = st.columns([4, 2, 4])
      with col1a:
          pass
      with col2a:
        st.write(f"#### {len(applied_filters_resorts)} resorts")
      with col3a:
          pass
      
      ## Sorting
      if 'sort' in st.session_state:
          sort_option = st.session_state['sort']
          reverse = False
          if sort_option == "Resort Name (A-Z)":
              key_func = lambda x: x['resort']
          elif sort_option == "Resort Name (Z-A)":
              key_func = lambda x: x['resort']
              reverse = True
          elif sort_option == "Overall Score (High to Low)":
              key_func = lambda x: get_overall_score(x)[0]
              reverse = True
          elif sort_option == "Overall Score (Low to High)":
              key_func = lambda x: get_overall_score(x)[0]
          else:
              key_func = None

          if key_func is not None:
              
              applied_filters_resorts = sorted(applied_filters_resorts, key=key_func, reverse=reverse)
      for resort in applied_filters_resorts:
          display_resort_card(resort['id'])