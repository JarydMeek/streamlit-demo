import streamlit as st

v1_page = st.Page('v1.py', title="Snow Report v1")
v2_page = st.Page('v2.py', title="Snow Report v2")

pg = st.navigation([v1_page, v2_page])
pg.run()