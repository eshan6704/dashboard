import zipfile
import io
import pandas as pd
import requests
from datetime import datetime as dt
from . import persist  # your persist.py

NSE_FO_BASE = "https://archives.nseindia.com/content/fo"

# -------------------------------
# Helper for FO cache naming
# -------------------------------
def fo_cache_name(fo_date: str):
    return f"BHAV_{fo_date.replace('-', '')}"

def html_cache_name(symbol: str, fo_date: str):
    return f"HTML_{symbol}_{fo_date.replace('-', '')}"

# -------------------------------
# Fetch FO Bhavcopy (requests)
# -------------------------------
def fetch_fo_bhavcopy(fo_date: str) -> pd.DataFrame:
    date = dt.strptime(fo_date, "%d-%m-%Y").date()
    ymd = date.strftime("%Y%m%d")
    file_name = f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv"
    zip_name = f"{file_name}.zip"
    url = f"{NSE_FO_BASE}/{zip_name}"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"FO bhavcopy download failed ({r.status_code})")

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        if file_name not in z.namelist():
            raise RuntimeError("FO bhavcopy CSV missing inside zip")
        with z.open(file_name) as f:
            df = pd.read_csv(f)

    # Save FO dataframe via persist
    persist.save(fo_cache_name(fo_date), df, "pkl")
    return df

# -------------------------------
# Option Chain Builder
# -------------------------------
def build_option_chain(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "ClsPric": "close",
        "PrvsClsgPric": "pre",
        "OpnIntrst": "oi",
        "ChngInOpnIntrst": "oi_chg",
        "TtlTradgVol": "vol"
    }

    df = df.rename(columns=rename)
    ce = df[df["OptnTp"] == "CE"].rename(columns={c: f"ce_{c}" for c in df.columns})
    pe = df[df["OptnTp"] == "PE"].rename(columns={c: f"pe_{c}" for c in df.columns})

    chain = pd.merge(
        ce, pe,
        left_on="ce_StrkPric",
        right_on="pe_StrkPric",
        how="outer"
    )
    chain["StrkPric"] = chain["ce_StrkPric"].combine_first(chain["pe_StrkPric"])

    keep = [
        "ce_oi", "ce_oi_chg", "ce_vol", "ce_close", "ce_pre",
        "StrkPric",
        "pe_pre", "pe_close", "pe_vol", "pe_oi_chg", "pe_oi"
    ]
    out = chain[keep].fillna(0).sort_values("StrkPric")
    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    return out.reset_index(drop=True)

# -------------------------------
# Main HTML builder with persist
# -------------------------------
def nse_fno_html(fo_date: str, symbol: str) -> str:
    html_name = html_cache_name(symbol, fo_date)
    fo_name = fo_cache_name(fo_date)

    # 1️⃣ Check if HTML exists
    if persist.exists(html_name, "html"):
        html = persist.load(html_name, "html")
        if html:
            return html

    # 2️⃣ Check if FO dataframe exists
    if persist.exists(fo_name, "pkl"):
        fo_df = persist.load(fo_name, "pkl")
    else:
        fo_df = fetch_fo_bhavcopy(fo_date)

    if fo_df.empty:
        html = "<h3>FO Bhavcopy empty</h3>"
        persist.save(html_name, html, "html")
        return html

    fo = fo_df.copy()
    exp = pd.to_datetime(fo["FininstrmActlXpryDt"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    monthly = exp[exp >= today].groupby([exp.dt.year, exp.dt.month]).max()
    if monthly.empty:
        html = "<h3>No valid expiry</h3>"
        persist.save(html_name, html, "html")
        return html

    expiry = monthly.iloc[0].strftime("%d-%m-%Y")
    fo["EXP"] = exp.dt.strftime("%d-%m-%Y")

    df = fo[(fo["TckrSymb"] == symbol) & (fo["EXP"] == expiry)]
    if df.empty:
        html = f"<h3>No F&O data for {symbol}</h3>"
        persist.save(html_name, html, "html")
        return html

    fut_df = df[df["FinInstrmTp"].isin(["STF", "IDF"])]
    opt_df = df[df["FinInstrmTp"].isin(["STO", "IDO"])]
    opt_chain = build_option_chain(opt_df)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: Arial; margin: 12px; background:#f5f5f5; }}
table {{ border-collapse: collapse; width: 100%; background:white; }}
th, td {{ border:1px solid #bbb; padding:6px; text-align:center; }}
th {{ background:#2e7d32; color:white; }}
h2,h3,h4 {{ margin:6px 0; }}
</style>
</head>
<body>

<h2>NSE F&O : {symbol}</h2>
<h4>Expiry: {expiry}</h4>

<h3>Futures</h3>
{fut_df.to_html(index=False) if not fut_df.empty else "<i>No Futures</i>"}

<h3>Option Chain</h3>
{opt_chain.to_html(index=False) if not opt_chain.empty else "<i>No Options</i>"}

</body>
</html>
"""

    return html
