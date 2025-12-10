import pandas as pd
import datetime

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
        print(df)
    except:
        return f"<h3>No Bhavcopy found for {date_str}.</h3>"

    # -------------------------------------------------------
    # 3) Rename columns
    # -------------------------------------------------------
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
        "DELIV_QTY": "del",
        "DELIV_PER": "perdel",
    }

    df = df.rename(columns=rename_map)

    # -------------------------------------------------------
    # 4) Select required columns
    # -------------------------------------------------------
    required = [
        "symbol","series","preclose","open","high",
        "low","close","volume","turnover","order","perdel"
    ]

    # ensure missing ones are created
    for col in required:
        if col not in df.columns:
            df[col] = 0

    df = df[required]

    # -------------------------------------------------------
    # 5) Add new computed columns
    # -------------------------------------------------------
    df["change"] = df["close"] - df["preclose"]
    df["perchange"] = (df["change"] / df["preclose"].replace(0, 1)) * 100
    df["pergap"] = ((df["open"] - df["preclose"]) / df["preclose"].replace(0, 1)) * 100

    # -------------------------------------------------------
    # 6) Build MAIN TABLE
    # -------------------------------------------------------
    main_html = df.to_html(index=False, escape=False)

    # -------------------------------------------------------
    # 7) Build GRID TABLES (5 columns)
    # -------------------------------------------------------
    df_sorted = df.sort_values("perchange", ascending=False)

    n = len(df_sorted)
    chunk_size = (n + 4) // 5
    chunks = [df_sorted.iloc[i:i+chunk_size] for i in range(0, n, chunk_size)]

    # each chunk to HTML
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
    # 8) CSS for layout
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
    # 9) Final Combined Output
    # -------------------------------------------------------
    return css + "<h2>Main Bhavcopy Table</h2>" + main_html + "<h2>5-Column Grid View</h2>" + grid_html
