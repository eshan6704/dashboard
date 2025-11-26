# common.py
import datetime

def format_large_number(num):
    if not isinstance(num, (int, float)):
        return num  # Return as-is if not a number
    sign = '-' if num < 0 else ''
    num = abs(float(num))
    if num >= 1_000_000_000_000:
        return f"{sign}{num / 1_000_000_000_000:.2f} LCr"
    elif num >= 10_000_000:
        return f"{sign}{num / 10_000_000:.2f} Cr"
    elif num >= 100_000:
        return f"{sign}{num / 100_000:.2f} Lac"
    else:
        return f"{sign}{num:,.0f}"

def format_timestamp_to_date(timestamp):
    if not isinstance(timestamp, (int, float)) or timestamp <= 0:
        return "N/A"
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid Date"
