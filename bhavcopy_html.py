import datetime
from nsepython import *

def fetch_bhavcopy_html(date_str):
    """
    Use existing nse_bhavcopy function to fetch Bhavcopy and return HTML directly.
    """
    # Validate date format
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return "<h3>Invalid date format. Please use DD-MM-YYYY.</h3>"

    # Fetch data using existing function
    try:
        df = nse_bhavcopy(date_str)
        # Convert DataFrame to HTML directly
        html = df.to_html(index=False, escape=False)
        return html
    except Exception:
        return f"<h3>No Bhavcopy found for {date_str}. Please check the date.</h3>"
