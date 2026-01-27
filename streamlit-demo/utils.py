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

  
def get_overall_score(resort):
    open_trails = float(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[0])
    total_trails = float(resort.get("open_trails", '0/0').replace('n/a', '0/0').split("/")[1])
    open_trails_percent = (open_trails / total_trails * 100) if total_trails > 0 else 0
    open_lifts = float(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[0])
    total_lifts = float(resort.get("open_lifts", '0/0').replace('n/a', '0/0').split("/")[1])
    open_lifts_percent = (open_lifts / total_lifts * 100) if total_lifts > 0 else 0
    overall_score = (open_trails_percent + open_lifts_percent) / 2
    return overall_score, get_score(overall_score)