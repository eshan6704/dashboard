import datetime
from nsepython import *
import pandas as pd

def build_column_tables(df, metric):
    """Return HTML for 5-column grid with scrollable tables."""

    # Sort by metric descending
    df_sorted = df.sort_values(metric, ascending=False)

    # Split into 5 equal chunks
    chunks = []
    size = (len(df_sorted) + 4) // 5  # ceil
    for i in range(0, len(df_sorted), size):
        chunks.append(df_sorted.iloc[i:i + size])

    # Build HTML grid
    html = "<div class='grid5'>"

    for chunk in chunks:
        html += "<div class='colbox'><table>"
        html += "<tr><th>Symbol</th><th>{}</th></tr>".format(metric.upper())
        for _, r in chunk.iterrows():
            html += f"<tr><td>{r['symbol']}</td><td>{r[metric]:.2f}</td></tr>"
        html += "</table></div>"

    html += "</div>"
    return html


def build_bhavcopy_html(date_str):
    """Bhavcopy + 5-column grid scroll-tables for perchange/turnover/order/volume/perdel"""

    # Validate date
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return "<h3>Invalid date format. Use DD-MM-YYYY.</h3>"

    try:
        df = nse_bhavcopy(date_str)

        # Rename columns
        df = df.rename(columns={
            "SYMBOL": "symbol", "SERIES": "series",
            "PREV_CLOSE": "preclose", "OPEN_PRICE": "open",
            "HIGH_PRICE": "high", "LOW_PRICE": "low",
            "CLOSE_PRICE": "close",
            "TTL_TRD_QNTY": "volume", "TURNOVER_LACS": "turnover",
            "NO_OF_TRADES": "order", "DELIV_PER": "perdel"
        })

        # Calculated fields
        df["change"] = df["close"] - df["preclose"]
        df["perchange"] = (df["change"] / df["preclose"]) * 100
        df["pergap"] = ((df["open"] - df["preclose"]) / df["preclose"]) * 100

        # Main table
        main_html = df.to_html(index=False)

        # Styles for 5-column grid & scrollable tables
        css = """
        <style>
        .grid5 {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin-top: 20px;
        }
        .colbox {
            max-height: 400px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 4px;
            background: white;
        }
        .colbox table {
            width: 100%;
            border-collapse: collapse;
        }
        .colbox th, .colbox td {
            border: 1px solid #ddd;
            padding: 4px;
            text-align: left;
            font-size: 13px;
        }
        .colbox th {
            background: #f0f0f0;
            font-weight: bold;
        }
        </style>
        """

        # Build 5-column grids for each metric
        metrics_html = ""
        for metric in ["perchange", "turnover", "order", "volume", "perdel"]:
            metrics_html += f"<h3>{metric.upper()}</h3>"
            metrics_html += build_column_tables(df, metric)

        final = f"""
        <h2>Bhavcopy : {date_str}</h2>
        {css}
        <h3>Main Table</h3>
        <div style='max-height:350px; overflow-y:scroll'>{main_html}</div>
        <h2>Matrix Tables (5 Columns Grid)</h2>
        {metrics_html}
        """

        return final

    except Exception:
        return f"<h3>No Bhavcopy found for {date_str}.</h3>"
