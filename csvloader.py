# ==============================
# Imports
# ==============================
import requests
import zipfile
from io import BytesIO, StringIO
from datetime import datetime as dt
from typing import Dict, Union

import pandas as pd

from persist import exists, load, save


# ==============================
# Raw CSV Loader (NO parsing)
# ==============================
def load_csv(url: str) -> Union[str, Dict[str, str]]:
    """
    Pure transport loader
    - .csv -> raw CSV text (str)
    - .zip -> {filename: raw CSV text}

    NO parsing
    NO cleaning
    NO assumptions
    """
    r = requests.get(url)
    r.raise_for_status()

    if url.lower().endswith(".zip"):
        z = zipfile.ZipFile(BytesIO(r.content))
        out: Dict[str, str] = {}

        for name in z.namelist():
            if name.lower().endswith(".csv"):
                with z.open(name) as f:
                    out[name] = f.read().decode("utf-8", errors="ignore")
        return out

    return r.text


# ==============================
# NSE High-Low HTML Formatter
# ==============================
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


# ==============================
# NSE High-Low Master Function
# ==============================
def nse_highlow(date_str: str | None = None) -> str:
    """
    Master NSE High-Low function

    Responsibilities:
    - Knows NSE CSV structure
    - Header starts at row index 2 (skip 0 & 1)
    - Uses raw CSV loader
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

    # 1️⃣ Load raw CSV text
    csv_text = load_csv(url)

    # 2️⃣ NSE-specific parsing (header row = 2)
    df = pd.read_csv(
        StringIO(csv_text),
        header=2
    )

    # 3️⃣ Build HTML
    html = _highlow_html_formatter(df, date_str)

    # 4️⃣ Persist HTML only
    save(cache_key, html, "html")

    return html