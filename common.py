# common.py
import datetime

# --- Shared CSS for all modules ---
STYLE_BLOCK = """
<style>
.styled-table {
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 0.9em;
  font-family: sans-serif;
  width: 100%;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.styled-table th, .styled-table td {
  padding: 8px 10px;
  border: 1px solid #ddd;
}
.styled-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}
.card {
  width: 95%;
  margin: 10px auto;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.card h2 {
  margin-top:0;
}
.big-box {
  width:95%;
  margin:20px auto;
  padding:20px;
  border:1px solid #ccc;
  border-radius:8px;
  background:#fff;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);
  font-size:0.95em;
  line-height:1.4em;
  max-height:400px;
  overflow-y:auto;
}
.key-value-pair {
  flex: 1 1 calc(20% - 15px);
  box-sizing: border-box;
  min-width: 150px;
  background: #fff;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.key-value-pair h3 {
  font-size: 0.95em;
  color: #444;
  margin: 0 0 5px 0;
}
.key-value-pair p {
  font-size: 0.9em;
  color: #555;
  margin: 0;
  font-weight: bold;
}
</style>
"""

# --- Shared utility functions ---
def format_large_number(num):
    if not isinstance(num, (int, float)):
        return num
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

def wrap_html(title, content_html, style_block=None):
    """Wrap content in a full HTML page with optional CSS."""
    style = style_block if style_block else STYLE_BLOCK
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    {style}
</head>
<body>
    {content_html}
</body>
</html>
"""
