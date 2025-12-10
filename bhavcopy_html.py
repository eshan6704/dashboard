import pandas as pd
import datetime
from nsepython import *

def build_bhavcopy_html(date_str):
    # -------------------------------------------------------
    # 1) Validate Date
    # -------------------------------------------------------
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return "<h3>Invalid date format. Use DD-MM-YYYY.</h3>"

    # -------------------------------------------------------
    # 2) Fetch Bhavcopy
    # -------------------------------------------------------
    try:
        df = nse_bhavcopy(date_str)   # <-- your custom loader
        df.columns = df.columns.str.strip()
    except:
        return f"<h3>No Bhavcopy found for {date_str}.</h3>"

    # -------------------------------------------------------
    # 3) Drop unwanted columns safely
    # -------------------------------------------------------
    remove = ["DATE1", "LAST_PRICE", "AVG_PRICE"]
    df.drop(columns=[col for col in remove if col in df.columns], inplace=True)

    # -------------------------------------------------------
    # 4) Convert numeric columns properly
    # -------------------------------------------------------
    numeric_cols = [
        "PREV_CLOSE",
        "OPEN_PRICE",
        "HIGH_PRICE",
        "LOW_PRICE",
        "CLOSE_PRICE",
        "TTL_TRD_QNTY",
        "TURNOVER_LACS",
        "NO_OF_TRADES",
        "DELIV_QTY",
        "DELIV_PER"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------------------------------------------------------
    # 5) Filter by turnover
    # -------------------------------------------------------
    df = df[df["TURNOVER_LACS"] > 1000]
    df = df.sort_values(by="TURNOVER_LACS", ascending=False)
    # -------------------------------------------------------
    # 6) Add computed columns
    # -------------------------------------------------------
    df["change"] = df["CLOSE_PRICE"] - df["PREV_CLOSE"]
    df["perchange"] = (df["change"] / df["PREV_CLOSE"].replace(0, 1)) * 100
    df["pergap"] = ((df["OPEN_PRICE"] - df["PREV_CLOSE"]) / df["PREV_CLOSE"].replace(0, 1)) * 100

    # -------------------------------------------------------
    # 7) MAIN TABLE (vertical scroll)
    # -------------------------------------------------------
    main_html = f"""
    <div class="main-table-container">
        {df.to_html(index=False, escape=False)}
    </div>
    """

    # -------------------------------------------------------
    # 8) GRID TABLE (SYMBOL vs metric)
    # -------------------------------------------------------
    metrics = ["perchange", "pergap", "TURNOVER_LACS", "NO_OF_TRADES", "DELIV_PER"]
    existing_metrics = [m for m in metrics if m in df.columns]

    col_html = []
    for metric in existing_metrics:
        temp_df = df[["SYMBOL", metric]].sort_values(metric, ascending=False)
        col_html.append(
            f"""
            <div class="col">
                <h4>{metric}</h4>
                {temp_df.to_html(index=False, escape=False)}
            </div>
            """
        )

    grid_html = """
    <div class="grid">
        """ + "\n".join(col_html) + """
    </div>
    """

    # -------------------------------------------------------
    # 9) CSS (improved header style)
    # -------------------------------------------------------
    css = """
    <style>
        .grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .col {
            max-height: 480px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 4px;
            background: #fafafa;
        }
        .main-table-container {
            max-height: 480px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 4px;
            background: #fff;
            margin-bottom: 20px;
        }
        table {
            font-size: 12px;
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            padding: 4px 8px;
            border: 1px solid #ddd;
        }
        th {
            background: linear-gradient(to bottom, #4CAF50, #2E7D32);
            color: white;
            font-weight: bold;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 3;
            box-shadow: 0 2px 2px -1px rgba(0,0,0,0.4);
        }
        td {
            text-align: right;
        }
    </style>
    """

    # -------------------------------------------------------
    # 10) Final Output
    # -------------------------------------------------------
    return (
        css +
        "<h2>Main Bhavcopy Table</h2>" +
        main_html +
        "<h2>Matrix/Grid Table</h2>" +
        grid_html
    )
