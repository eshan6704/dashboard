# build_nse_fno.py
import os
import subprocess
import zipfile
import tempfile
import pandas as pd
from datetime import datetime as dt

from .persist import exists, load, save


NSE_FO_BASE = "https://archives.nseindia.com/content/fo"


# ============================================================
# FETCH FO BHAVCOPY (RAW DF)
# ============================================================
def _fetch_fo_bhavcopy(fo_date: str) -> pd.DataFrame:
    """
    fo_date format : DD-MM-YYYY
    """
    date = dt.strptime(fo_date, "%d-%m-%Y").date()
    ymd = date.strftime("%Y%m%d")

    file_name = f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv"
    zip_name = f"{file_name}.zip"
    url = f"{NSE_FO_BASE}/{zip_name}"

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, zip_name)

        cmd = [
            "curl", "-L",
            "-A", "Mozilla/5.0",
            "--tlsv1.2",
            "--compressed",
            "-o", zip_path,
            url
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if res.returncode != 0 or not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1024:
            raise RuntimeError("FO bhavcopy download failed")

        with zipfile.ZipFile(zip_path) as z:
            if file_name not in z.namelist():
                raise RuntimeError("FO bhavcopy csv missing inside zip")

            with z.open(file_name) as f:
                return pd.read_csv(f)


# ============================================================
# OPTION CHAIN BUILDER
# ============================================================
def _build_option_chain(df: pd.DataFrame) -> pd.DataFrame:
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


# ============================================================
# MAIN HTML BUILDER
# ============================================================
def build_nse_fno_html(fo_date: str, symbol: str) -> str:
    """
    Returns HTML ONLY
    """

    date_key = dt.strptime(fo_date, "%d-%m-%Y").strftime("%Y%m%d")
    cache_html = f"NSE_FNO_HTML_{date_key}_{symbol}"
    cache_df   = f"NSE_FNO_BHAVCOPY_{date_key}"

    # ================= HTML CACHE =================
    if exists(cache_html, "html"):
        cached = load(cache_html, "html")

        if isinstance(cached, str):
            return cached

        if isinstance(cached, pd.DataFrame):
            return cached.to_html(index=False)

    # ================= BHAVCOPY CACHE =================
    if exists(cache_df):
        fo_df = load(cache_df)
    else:
        fo_df = _fetch_fo_bhavcopy(fo_date)
        save(cache_df, fo_df)

    if not isinstance(fo_df, pd.DataFrame) or fo_df.empty:
        return "<h3>Invalid FO Bhavcopy</h3>"

    # ================= PROCESS =================
    fo = fo_df.copy()

    exp = pd.to_datetime(fo["FininstrmActlXpryDt"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    monthly = exp[exp >= today].groupby([exp.dt.year, exp.dt.month]).max()
    if monthly.empty:
        return "<h3>No valid expiry</h3>"

    expiry = monthly.iloc[0].strftime("%d-%m-%Y")
    fo["EXP"] = exp.dt.strftime("%d-%m-%Y")

    df = fo[(fo["TckrSymb"] == symbol) & (fo["EXP"] == expiry)]
    if df.empty:
        return f"<h3>No F&O data for {symbol}</h3>"

    fut_df = df[df["FinInstrmTp"].isin(["STF", "IDF"])]
    opt_df = df[df["FinInstrmTp"].isin(["STO", "IDO"])]

    opt_chain = _build_option_chain(opt_df)

    # ================= HTML =================
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

    # ================= SAVE =================
    save(cache_html, html, "html")
    return html
