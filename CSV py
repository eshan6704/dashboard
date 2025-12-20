# CSV.py

import pandas as pd
import requests
import zipfile
from io import BytesIO
from datetime import datetime as dt
from typing import List, Union

from persist import exists, load, save


def load_csv(
    url: str,
    header_row: int = 0,
    text_cols: List[str] | None = None
) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    """
    Load CSV or ZIP containing CSVs
    - .csv -> DataFrame
    - .zip -> List[DataFrame]
    """
    text_cols = text_cols or []

    def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.columns = (
            df.columns
            .str.strip()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        for col in df.columns:
            if col not in text_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.dropna(how="all")

    if url.lower().endswith(".zip"):
        r = requests.get(url)
        r.raise_for_status()
        z = zipfile.ZipFile(BytesIO(r.content))
        dfs = []
        for name in z.namelist():
            if name.lower().endswith(".csv"):
                with z.open(name) as f:
                    df = pd.read_csv(f, header=header_row)
                    dfs.append(_clean_df(df))
        return dfs

    df = pd.read_csv(url, header=header_row)
    return _clean_df(df)


def _highlow_html_formatter(df: pd.DataFrame, date_str: str) -> str:
    metric = "PERCENT_CHANGE"
    df_html = df.copy()

    top_up = df[metric].nlargest(3).index if metric in df else []
    top_dn = df[metric].nsmallest(3).index if metric in df else []

    for idx, row in df_html.iterrows():
        for col in df_html.columns:
            val = row[col]
            style = ""
            if isinstance(val, (int, float)):
                txt = f"{val:.2f}"
                if val > 0:
                    style = "pos"
                elif val < 0:
                    style = "neg"
                if col == metric:
                    if idx in top_up:
                        style += " top-up"
                    elif idx in top_dn:
                        style += " top-down"
                df_html.at[idx, col] = f'<span class="{style.strip()}">{txt}</span>'
            else:
                df_html.at[idx, col] = str(val)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NSE High-Low {date_str}</title>
<style>
body {{ font-family: Arial; background:#f5f5f5; padding:12px; }}
table {{ border-collapse: collapse; width:100%; background:white; }}
th, td {{ border:1px solid #bbb; padding:6px; font-size:13px; }}
th {{ background:#222; color:white; }}
.pos {{ color:green; font-weight:bold; }}
.neg {{ color:red; font-weight:bold; }}
.top-up {{ background:#b6f2b6; }}
.top-down {{ background:#f2b6b6; }}
</style>
</head>
<body>
<h2>NSE Index High / Low — {date_str}</h2>
{df_html.to_html(index=False, escape=False)}
</body>
</html>
"""


def nse_highlow(date_str: str | None = None) -> str:
    """
    Master NSE High-Low function
    - Uses load_csv
    - Builds HTML
    - Persists ONLY HTML
    """
    if not date_str:
        date_str = dt.now().strftime("%d-%m-%Y")

    cache_key = f"highlow_{date_str}"

    if exists(cache_key, "html"):
        return load(cache_key, "html")

    d = dt.strptime(date_str, "%d-%m-%Y")
    url = (
        "https://archives.nseindia.com/content/indices/"
        f"ind_close_all_{d.strftime('%d%m%Y')}.csv"
    )

    df = load_csv(
        url=url,
        header_row=2,
        text_cols=["Index_Name", "Index_Date"]
    )

    html = _highlow_html_formatter(df, date_str)
    save(cache_key, html, "html")
    return html