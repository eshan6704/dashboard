import datetime
from nsepython import *
import pandas as pd

def build_bhavcopy_html(date_str):

    # --- Validate ---
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return "<h3>Invalid date. Use DD-MM-YYYY.</h3>"

    # --- Fetch ---
    try:
        df = nse_bhavcopy(date_str)
    except Exception as e:
        return f"<h3>Error fetching bhavcopy: {e}</h3>"

    # --- Rename Columns ---
    rename_map = {
        "SYMBOL": "symbol",
        "SERIES": "series",
        "PREV_CLOSE": "preclose",
        "OPEN_PRICE": "open",
        "HIGH_PRICE": "high",
        "LOW_PRICE": "low",
        "CLOSE_PRICE": "close",
        "TTL_TRD_QNTY": "volume",
        "TURNOVER_LACS": "turnover",
        "NO_OF_TRADES": "order",
        "DELIV_PER": "perdel"
    }

    # rename only existing
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})

    # --- Filter Only Required Columns ---
    required = [
        "symbol","series","preclose","open","high",
        "low","close","volume","turnover","order","perdel"
    ]

    # fill missing columns safely
    for col in required:
        if col not in df.columns:
            df[col] = 0

    df = df[required]

    # --- Add Computed Columns ---
    df["change"]    = df["close"] - df["preclose"]
    df["perchange"] = (df["change"] / df["preclose"].replace(0, 1)) * 100
    df["pergap"]    = ((df["open"] - df["preclose"]) / df["preclose"].replace(0, 1)) * 100

    # --- Prepare for Grid ---
    df_sorted = df.sort_values("perchange", ascending=False)[["symbol", "perchange"]]

    n = len(df_sorted)
    chunk_size = (n + 4)//5      # divide into 5 equal parts

    chunks = [df_sorted.iloc[i:i+chunk_size] for i in range(0, n, chunk_size)]

    # --- Build HTML ---
    css = """
    <style>
        .grid5 {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .colbox {
            max-height: 500px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 6px;
            background: #fff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 4px;
            text-align: left;
        }
        th {
            background: #f4f4f4;
        }
    </style>
    """

    html = f"<h2>Bhavcopy Grid – {date_str}</h2>{css}"
    html += "<div class='grid5'>"

    for chunk in chunks:
        html += "<div class='colbox'><table>"
        html += "<tr><th>Symbol</th><th>% Chg</th></tr>"
        for _, row in chunk.iterrows():
            html += f"<tr><td>{row['symbol']}</td><td>{row['perchange']:.2f}</td></tr>"
        html += "</table></div>"

    html += "</div>"

    return html
