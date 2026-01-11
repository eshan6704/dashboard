# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback
from . import persist

# ============================================================
# DAILY DATA FETCH (DO NOT CHANGE)
# ============================================================
def daily(symbol, date_end, date_start):
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

    df = yf.download(symbol + ".NS", start=start, end=end)

    # Flatten multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns.name = None
    df.index.name = "Date"
    return df


# ============================================================
# DASHBOARD
# ============================================================
def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df is None or df.empty:
            return "<h1>No data</h1>"

        # -------------------------------
        # CLEAN & FORMAT
        # -------------------------------
        df = df.reset_index()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # -------------------------------
        # TABLE HTML
        # -------------------------------
        table_rows = ""
        for i, r in df.iterrows():
            color = "#e8f5e9" if i % 2 == 0 else "#f5f5f5"
            table_rows += f"""
            <tr style="background:{color}">
                <td>{r['DateStr']}</td>
                <td>{r['Open']:.2f}</td>
                <td>{r['High']:.2f}</td>
                <td>{r['Low']:.2f}</td>
                <td>{r['Close']:.2f}</td>
                <td>{int(r['Volume'])}</td>
            </tr>
            """

        table_html = f"""
        <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Date</th><th>Open</th><th>High</th>
                    <th>Low</th><th>Close</th><th>Volume</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        </div>
        """

        # -------------------------------
        # FULL HTML (IMPORTANT)
        # -------------------------------
        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{symbol} Daily Dashboard</title>

<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 10px;
    background: #f4f6f9;
}}

.table-wrap {{
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 20px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    background: white;
}}

th {{
    position: sticky;
    top: 0;
    background: linear-gradient(to right,#1a4f8a,#4a7ac7);
    color: white;
    padding: 6px;
}}

td {{
    padding: 6px;
    text-align: right;
}}

td:first-child {{
    text-align: left;
}}
.chart {{
    margin-bottom: 30px;
}}
</style>
</head>

<body>

<h2>{symbol} – Daily Price Table</h2>
{table_html}

<h2>Candlestick & Volume</h2>
<div id="candle" class="chart"></div>

<h2>Moving Averages</h2>
<div id="ma" class="chart"></div>

<script>
const dates = {df["DateStr"].tolist()};
const openp = {df["Open"].round(2).tolist()};
const highp = {df["High"].round(2).tolist()};
const lowp  = {df["Low"].round(2).tolist()};
const closep= {df["Close"].round(2).tolist()};
const volume= {df["Volume"].astype(int).tolist()};
const ma20  = {df["MA20"].round(2).fillna(None).tolist()};
const ma50  = {df["MA50"].round(2).fillna(None).tolist()};

Plotly.newPlot("candle", [
    {{
        x: dates,
        open: openp,
        high: highp,
        low: lowp,
        close: closep,
        type: "candlestick",
        name: "Price"
    }},
    {{
        x: dates,
        y: volume,
        type: "bar",
        yaxis: "y2",
        name: "Volume",
        opacity: 0.3
    }}
], {{
    yaxis: {{title: "Price"}},
    yaxis2: {{overlaying: "y", side: "right", title: "Volume"}},
    xaxis: {{rangeslider: {{visible:false}}}}
}});

Plotly.newPlot("ma", [
    {{x: dates, y: closep, type:"scatter", name:"Close"}},
    {{x: dates, y: ma20, type:"scatter", name:"MA20"}},
    {{x: dates, y: ma50, type:"scatter", name:"MA50"}}
]);
</script>

</body>
</html>
"""

        persist.save(key, html, "html")
        return html

    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>"
