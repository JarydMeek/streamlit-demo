import streamlit as st

def get_score(percent):
    if percent == 100:
        return "A+"
    if percent >= 90:
        return "A"
    elif percent >= 75:
        return "B"
    elif percent >= 50:
        return "C"
    elif percent >= 25:
        return "D"
    else:
        return "F"

def get_score_color(score):
    colors = {
        "A+": "#28a745",
        "A": "#28a745",
        "B": "#5cb85c",
        "C": "#ffc107",
        "D": "#fd7e14",
        "F": "#dc3545"
    }
    return colors.get(score, "#666")
    
def get_score_metric(percent, label):
    score = get_score(percent)
    color = get_score_color(score)
    
    st.markdown(f"""
        <p style="
            margin-bottom: 0;
        ">{label}: ({percent:.1f}%)</p>
        <p style="
            font-size: 2rem;
            font-weight: 600;
            color: {color};
            margin: 0;
        ">{score}</p>
    """, unsafe_allow_html=True)