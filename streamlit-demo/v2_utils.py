from datetime import datetime

def format_date(date_str):
    date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
    return date_obj.strftime("%b %d, %Y")