import streamlit as st

def get_open_popover_button():
  if 'sidebar_open' not in st.session_state:
      st.session_state['sidebar_open'] = False
  if st.button("Search & Filter"):
      st.session_state['sidebar_open'] = not st.session_state['sidebar_open']


def get_popover():
    open = st.session_state.get('sidebar_open', False);
    if open:
          with st.popover():
              st.write("## Search & Filter Options")
              st.markdown("# Overall Score")
          return True
    return False