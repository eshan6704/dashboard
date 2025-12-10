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
    # 2) Fetch using YOUR nse_bhavcopy definition
    # -------------------------------------------------------
    try:
        df = nse_bhavcopy(date_str)   # <-- your custom loader
    except:
        return f"<h3>No Bhavcopy found for {date_str}.</h3>"


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
"
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
    # 6) Add computed columns
    # -------------------------------------------------------
    df["change"] = df["CLOSE_PRICE"] - df["PREV_CLOSE"]
    df["perchange"] = (df["change"] / df["PREV_CLOSE"].replace(0, 1)) * 100
    df["pergap"] = ((df["OPEN_PRICE"] - df["PREV_CLOSE"]) / df["PREV_CLOSE"].replace(0, 1)) * 100
    print(df)
    
    # -------------------------------------------------------
    # 7) MAIN TABLE
    # -------------------------------------------------------
    main_html = df.to_html(index=False, escape=False)

    # -------------------------------------------------------
    # 8) GRID TABLE (5 columns)
    # -------------------------------------------------------
    df_sorted = df.sort_values("perchange", ascending=False)

    n = len(df_sorted)
    chunk_size = (n + 4) // 5
    chunks = [df_sorted.iloc[i:i+chunk_size] for i in range(0, n, chunk_size)]

    col_html = []
    for ch in chunks:
        col_html.append(
            f"""
            <div class="col">
                {ch.to_html(index=False, escape=False)}
            </div>
            """
        )

    grid_html = """
    <div class="grid">
        """ + "\n".join(col_html) + """
    </div>
    """

    # -------------------------------------------------------
    # 9) CSS
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
        table {
            font-size: 12px;
            border-collapse: collapse;
        }
        th, td {
            padding: 3px 6px;
            border: 1px solid #ddd;
        }
        th {
            background: #eee;
            position: sticky;
            top: 0;
            z-index: 1;
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
        "<h2>5-Column Grid View</h2>" +
        grid_html
    )
