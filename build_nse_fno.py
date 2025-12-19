# fno.py
import os
import subprocess
import zipfile
import pandas as pd
import datetime as dt
import tempfile
import pickle

# ============================================================
# CONFIG
# ============================================================
CACHE_DIR = "./cache/fno"
os.makedirs(CACHE_DIR, exist_ok=True)


# ============================================================
# CACHE HELPERS (DATE-BASED)
# ============================================================
def _cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.pkl")


def exists(key):
    return os.path.exists(_cache_path(key))


def load(key):
    try:
        with open(_cache_path(key), "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def save(key, obj):
    with open(_cache_path(key), "wb") as f:
        pickle.dump(obj, f)


# ============================================================
# FETCH FO BHAVCOPY (RAW)
# ============================================================
def fo_bhavcopy(date_input) -> pd.DataFrame:
    """
    Download NSE F&O bhavcopy for a given date
    date_input: dd-mm-yyyy | datetime.date | datetime.datetime
    """
    if isinstance(date_input, str):
        date = dt.datetime.strptime(date_input, "%d-%m-%Y").date()
    elif isinstance(date_input, dt.datetime):
        date = date_input.date()
    elif isinstance(date_input, dt.date):
        date = date_input
    else:
        raise ValueError("Invalid date format. Use dd-mm-yyyy")

    ymd = date.strftime("%Y%m%d")
    file_name = f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv"
    zip_name = f"{file_name}.zip"
    url = f"https://nsearchives.nseindia.com/content/fo/{zip_name}"

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, zip_name)

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
            raise RuntimeError("FO Bhavcopy download failed or blocked")

        with zipfile.ZipFile(zip_path) as z:
            with z.open(file_name) as f:
                df = pd.read_csv(f)

    return df


# ============================================================
# OPTION CHAIN BUILDER
# ============================================================
def build_option_chain(opt_df: pd.DataFrame) -> pd.DataFrame:
    drop = [
        "FininstrmActlXpryDt", "FinInstrmTp", "TckrSymb",
        "TtlNbOfTxsExctd", "NewBrdLotQty",
        "EXP_DMY", "SttlmPric",
        "OpnPric", "HghPric", "LwPric", "TtlTrfVal"
    ]

    rename = {
        "ClsPric": "close",
        "PrvsClsgPric": "pre",
        "OpnIntrst": "oi",
        "ChngInOpnIntrst": "oi_chg",
        "TtlTradgVol": "vol"
    }

    opt_df = opt_df.drop(drop, axis=1, errors="ignore").rename(columns=rename)

    ce = opt_df[opt_df["OptnTp"] == "CE"].rename(
        columns={c: f"ce_{c}" for c in opt_df.columns}
    )
    pe = opt_df[opt_df["OptnTp"] == "PE"].rename(
        columns={c: f"pe_{c}" for c in opt_df.columns}
    )

    chain = pd.merge(
        ce, pe,
        left_on="ce_StrkPric",
        right_on="pe_StrkPric",
        how="outer"
    )

    chain["StrkPric"] = chain["ce_StrkPric"].combine_first(chain["pe_StrkPric"])

    chain.drop(
        columns=[
            "ce_StrkPric", "pe_StrkPric",
            "ce_OptnTp", "pe_OptnTp",
            "ce_UndrlygPric", "pe_UndrlygPric"
        ],
        inplace=True,
        errors="ignore"
    )

    chain = chain.fillna(0).sort_values("StrkPric").reset_index(drop=True)

    cols = [
        "ce_oi", "ce_oi_chg", "ce_vol", "ce_close", "ce_pre",
        "StrkPric",
        "pe_pre", "pe_close", "pe_vol", "pe_oi_chg", "pe_oi"
    ]

    df = chain[cols].copy()

    for c in ["ce_close", "ce_pre", "pe_close", "pe_pre"]:
        df[c] = df[c].astype(float).round(2)

    for c in [
        "ce_oi", "ce_oi_chg", "ce_vol",
        "pe_vol", "pe_oi_chg", "pe_oi", "StrkPric"
    ]:
        df[c] = df[c].astype(int)

    return df


# ============================================================
# HTML TABLE RENDER
# ============================================================
def df_to_html(df: pd.DataFrame, title=None) -> str:
    style = """
    <style>
        table {border-collapse: collapse; width:100%; font-family:Arial;}
        th, td {border:1px solid #ddd; padding:6px; text-align:center;}
        th {background:#2e7d32; color:white;}
        tr:nth-child(even){background:#f2f2f2;}
    </style>
    """

    html = df.to_html(index=False, escape=False)
    if title:
        html = f"<h3>{title}</h3>" + html

    return style + html


# ============================================================
# MAIN ENTRY (DAILY VALIDITY)
# ============================================================
def nse_fno_html(fo_date: str, symbol: str) -> str:
    """
    Daily-valid F&O HTML builder
    Cache rules:
    - HTML cached per (date + symbol)
    - FO bhavcopy cached per date
    """

    date_key = dt.datetime.strptime(fo_date, "%d-%m-%Y").strftime("%Y%m%d")

    html_key = f"fno_html_{date_key}_{symbol}"
    fo_key = f"fno_bhavcopy_{date_key}"

    # ---------------- HTML CACHE FIRST ----------------
    if exists(html_key):
        html = load(html_key)
        if html:
            return html

    # ---------------- FO CACHE ----------------
    if exists(fo_key):
        fo_df = load(fo_key)
    else:
        fo_df = fo_bhavcopy(fo_date)
        save(fo_key, fo_df)

    # ---------------- BUILD DATA ----------------
    fo = fo_df.copy().drop(
        ["ISIN", "Rmks", "SctySrs", "Rsvd1", "Rsvd2", "Rsvd3", "Rsvd4"],
        axis=1,
        errors="ignore"
    )

    exp = pd.to_datetime(fo["FininstrmActlXpryDt"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    monthly = (
        exp[exp >= today]
        .groupby([exp.dt.year, exp.dt.month])
        .max()
        .sort_values()
    )

    if monthly.empty:
        return "<h3>No valid expiry found</h3>"

    expiry = monthly.iloc[0].strftime("%d-%m-%Y")

    fo["EXP_DMY"] = exp.dt.strftime("%d-%m-%Y")

    df = fo[
        (fo["TckrSymb"] == symbol) &
        (fo["EXP_DMY"] == expiry)
    ].copy()

    if df.empty:
        return f"<h3>No F&O data for {symbol}</h3>"

    # ---------------- COMMON ----------------
    common_cols = [
        "TradDt", "BizDt", "Sgmt", "Src", "SsnId",
        "FinInstrmId", "XpryDt", "FinInstrmNm", "LastPric"
    ]

    common_df = pd.DataFrame([df.iloc[0][common_cols]])
    common_df.insert(0, "Expiry", expiry)

    # ---------------- FUTURE + OPTION ----------------
    future_df = df[df["FinInstrmTp"].isin(["STF", "IDF"])]
    option_df = df[df["FinInstrmTp"].isin(["STO", "IDO"])]

    option_chain_df = build_option_chain(option_df)

    html = (
        df_to_html(common_df, "Common Info") + "<br>"
        + df_to_html(future_df, "Future Contracts") + "<br>"
        + df_to_html(option_chain_df, "Option Chain")
    )

    # ---------------- SAVE HTML ----------------
    save(html_key, html)

    return html
