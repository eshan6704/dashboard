def build_bhav_html(df):
    if df is None or df.empty:
        return "<h3>No Bhavcopy Found</h3>"

    # ------------------------------
    # 1) RENAME + FILTER REQUIRED COLS
    # ------------------------------
    df = df.rename(columns={
        "CH_PREV_CLOSE": "preclose",
        "CH_OPENING_PRICE": "open",
        "CH_CLOSING_PRICE": "close",
        "CH_TOT_TRADED_QTY": "volume",
        "CH_TOT_TRADED_VAL": "turnover",
        "CH_LAST_TRADED_PRICE": "ltp",
        "CH_TRADED_ORDERS": "order",
        "CH_DELIV_QTY": "delqty",
        "CH_DELIV_PER": "perdel"
    })

    required = [
        "symbol","series","preclose","open","high","low",
        "close","volume","turnover","order","perdel"
    ]
    df = df[required].copy()

    # ------------------------------
    # 2) ADD NEW COLUMNS
    # ------------------------------
    df["change"] = df["close"] - df["preclose"]
    df["perchange"] = (df["change"] / df["preclose"] * 100).round(2)
    df["pergap"] = ((df["open"] - df["preclose"]) / df["preclose"] * 100).round(2)

    # Sorting for grid tables
    df_sorted = df.sort_values("perchange", ascending=False)

    # ------------------------------
    # 3) MAIN TABLE (top)
    # ------------------------------
    main_table_html = df.to_html(index=False, classes="main-table")

    # ------------------------------
    # 4) 5-COLUMN GRID (each column scrollable)
    # ------------------------------

    col_names = ["perchange", "turnover", "order", "volume", "perdel"]
    tables_html = ""

    for col in col_names:
        sub = df_sorted[["symbol", col]].copy()
        sub = sub.sort_values(col, ascending=False)
        tables_html += f"""
        <div class="grid-col">
            <h4>{col.upper()}</h4>
            <div class="grid-scroll">
                {sub.to_html(index=False, classes='sub-table')}
            </div>
        </div>
        """

    full_html = f"""
    <style>
        .main-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 18px;
        }}
        .main-table th, .main-table td {{
            padding: 6px 8px;
            border: 1px solid #ddd;
        }}

        /* GRID */
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            width: 100%;
        }}

        .grid-col {{
            background: white;
            border: 1px solid #ccc;
            padding: 6px;
            border-radius: 4px;
        }}

        .grid-scroll {{
            max-height: 420px;
            overflow-y: scroll;
        }}

        .sub-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .sub-table th, .sub-table td {{
            border: 1px solid #ddd;
            padding: 4px 6px;
            font-size: 13px;
        }}
    </style>

    <h3>Bhavcopy Table</h3>
    {main_table_html}

    <h3>Matrix Grid</h3>
    <div class="grid-container">
        {tables_html}
    </div>
    """

    return full_html
