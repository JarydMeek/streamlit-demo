import streamlit as st

def get_popover():
    if 'filter' not in st.session_state:
        st.session_state.filter = {}
    
    with st.popover("Sort & Filter"):
        st.write("## Sort By")
        st.selectbox("Select sorting option", [
            "Overall Score (High to Low)",
            "Overall Score (Low to High)",
            "Resort Name (A-Z)",
            "Resort Name (Z-A)",
        ], key="sort")

        st.write("## Filters")
        st.write("#### Overall Score")
        
        scores = ["A+", "A", "B", "C", "D", "F"]
        
        for score in scores:
            st.checkbox(score, key=f"score_{score}")
        
        # Build the filter object from checkbox states
        selected_scores = [
            score for score in scores 
            if st.session_state.get(f"score_{score}", False)
        ]
        st.session_state.filter['overall_score'] = selected_scores

        st.write("#### New Snow (24h)")

        st.toggle("Show Resorts with New Snow > 0 inches", key="filter_new_snow")

        st.session_state.filter['new_snow'] = st.session_state.get("filter_new_snow", False)


