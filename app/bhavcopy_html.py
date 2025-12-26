import pandas as pd
from . import nsepythonmodified as nse
from . import persist
from datetime import datetime as dt


def build_bhavcopy_html(date_str):
    key = f"bhavcopy_{date_str}"

    # -------------------------------------------------------
    # 0) Use cached HTML if present
    # -------------------------------------------------------
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(
                f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Using cached bhavcopy for {date_str}"
            )
            return cached

    try:
        # -------------------------------------------------------
        # 1) Validate Date (DD-MM-YYYY)
        # -------------------------------------------------------
        try:
            dt.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            html = "<h3>Invalid date format. Use DD-MM-YYYY.</h3>"
            persist.save(key, html, "html")
            return html

        # -------------------------------------------------------
        # 2) Fetch Bhavcopy (nsepython expects DD-MM-YYYY)
        # -------------------------------------------------------
        try:
            df = nse.nse_bhavcopy(date_str)
            df.columns = df.columns.str.strip()
        except Exception:
            html = f"<h3>No Bhavcopy found for {date_str}.</h3>"
            persist.save(key, html, "html")
            return html

        # -------------------------------------------------------
        # 3) Drop unwanted columns
        # -------------------------------------------------------
        remove = ["DATE1", "LAST_PRICE", "AVG_PRICE"]
        df.drop(columns=[c for c in remove if c in df.columns], inplace=True)

        # -------------------------------------------------------
        # 4) Convert numeric columns
        # -------------------------------------------------------
        numeric_cols = [
            "PREV_CLOSE", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE",
            "CLOSE_PRICE", "TTL_TRD_QNTY", "TURNOVER_LACS",
            "NO_OF_TRADES", "DELIV_QTY", "DELIV_PER"
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
        # 5) Filter & sort
        # -------------------------------------------------------
        df = df[df["TURNOVER_LACS"] > 1000]
        df = df.sort_values("TURNOVER_LACS", ascending=False)

        # -------------------------------------------------------
        # 6) Computed columns
        # -------------------------------------------------------
        df["change"] = df["CLOSE_PRICE"] - df["PREV_CLOSE"]
        df["perchange"] = (df["change"] / df["PREV_CLOSE"].replace(0, 1)) * 100
        df["pergap"] = (
            (df["OPEN_PRICE"] - df["PREV_CLOSE"]) /
            df["PREV_CLOSE"].replace(0, 1)
        ) * 100

        # -------------------------------------------------------
        # 7) HTML Output
        # -------------------------------------------------------
        main_html = f"""
        <div class="main-table-container">
            {df.to_html(index=False, escape=False)}
        </div>
        """

        metrics = ["perchange", "pergap", "TURNOVER_LACS", "NO_OF_TRADES", "DELIV_PER"]
        col_html = []

        for m in metrics:
            if m in df.columns:
                temp = df[["SYMBOL", m]].sort_values(m, ascending=False)
                col_html.append(
                    f"""
                    <div class="col">
                        <h4>{m}</h4>
                        {temp.to_html(index=False, escape=False)}
                    </div>
                    """
                )

        grid_html = f"""
        <div class="grid">
            {''.join(col_html)}
        </div>
        """

        css = """
        <style>
            .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
            .col, .main-table-container {
                max-height: 480px; overflow-y: auto;
                border: 1px solid #ccc; padding: 4px;
            }
            table { font-size: 12px; width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 4px; }
            th {
                background: #2E7D32; color: white;
                position: sticky; top: 0;
            }
        </style>
        """

        html = (
            css +
            "<h2>Main Bhavcopy Table</h2>" +
            main_html +
            "<h2>Matrix/Grid Table</h2>" +
            grid_html
        )

        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(
            f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Error build_bhavcopy_html: {e}"
        )
        return f"<h3>Error: {e}</h3>"