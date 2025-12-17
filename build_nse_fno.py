# build_nse_fno.py
import subprocess, zipfile, pandas as pd, datetime, os, tempfile

# ----------------- Fetch Bhavcopy -----------------
def fo_bhavcopy(date_input) -> pd.DataFrame:
    if isinstance(date_input, str):
        date = datetime.datetime.strptime(date_input, "%d-%m-%Y").date()
    elif isinstance(date_input, datetime.datetime):
        date = date_input.date()
    elif isinstance(date_input, datetime.date):
        date = date_input
    else:
        raise ValueError("Invalid date format. Use dd-mm-yyyy")
    
    ymd = date.strftime("%Y%m%d")
    file_name = f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv"
    zip_name = f"{file_name}.zip"
    url = f"https://nsearchives.nseindia.com/content/fo/{zip_name}"

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, zip_name)
        cmd = ["curl", "-L", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               "--tlsv1.2", "--compressed", "-o", zip_path, url]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0 or not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1024:
            raise RuntimeError("Download failed or blocked")
        with zipfile.ZipFile(zip_path) as z, z.open(file_name) as f:
            df = pd.read_csv(f)
    return df

# ----------------- Build Option Chain -----------------
def build_option_chain(opt_df):
    drop = ["FininstrmActlXpryDt","FinInstrmTp","TckrSymb","TtlNbOfTxsExctd",
            "NewBrdLotQty","EXP_DMY","SttlmPric",'OpnPric','HghPric','LwPric','TtlTrfVal']
    rename = {"ClsPric":"close","PrvsClsgPric":"pre","OpnIntrst":"oi",
              "ChngInOpnIntrst":"oi_chg","TtlTradgVol":"vol"}
    opt_df = opt_df.drop(drop, axis=1).rename(columns=rename)

    ce = opt_df[opt_df['OptnTp']=='CE'].rename(columns={c:f"ce_{c}" for c in opt_df.columns})
    pe = opt_df[opt_df['OptnTp']=='PE'].rename(columns={c:f"pe_{c}" for c in opt_df.columns})

    chain = pd.merge(ce, pe, left_on='ce_StrkPric', right_on='pe_StrkPric', how='outer')
    chain['StrkPric'] = chain['ce_StrkPric'].combine_first(chain['pe_StrkPric'])
    chain.drop(columns=['ce_StrkPric','pe_StrkPric','ce_OptnTp','pe_OptnTp','ce_UndrlygPric','pe_UndrlygPric'], inplace=True)
    chain = chain.fillna(0).sort_values('StrkPric').reset_index(drop=True)

    cols = ['ce_oi','ce_oi_chg','ce_vol','ce_close','ce_pre','StrkPric',
            'pe_pre','pe_close','pe_vol','pe_oi_chg','pe_oi']
    df = chain[cols].copy()
    for c in ['ce_close','ce_pre','pe_close','pe_pre']:
        df[c] = df[c].apply(lambda x: f"{x:.2f}")
    for c in ['ce_oi','ce_oi_chg','ce_vol','pe_vol','pe_oi_chg','pe_oi','StrkPric']:
        df[c] = df[c].astype(int)
    return df

# ----------------- HTML Rendering -----------------
def df_to_html(df, title=None):
    style = (
        "<style>"
        "table {border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;}"
        "th, td {border: 1px solid #ddd; padding: 8px; text-align: center;}"
        "th {background-color: #4CAF50; color: white;}"
        "tr:nth-child(even){background-color: #f2f2f2;}"
        "tr:hover {background-color: #ddd;}"
        "</style>"
    )
    html = df.to_html(index=False, escape=False)
    if title: html = f"<h3>{title}</h3>" + html
    return style + html

# ----------------- Main Combined Function -----------------
def nse_fno_html(fo_date, symbol):
    """
    Fetch NSE F&O data and return a single HTML string
    containing common, future, and option tables
    """
    fo_df = fo_bhavcopy(fo_date)
    fo = fo_df.copy().drop(['ISIN','Rmks','SctySrs','Rsvd1','Rsvd2','Rsvd3','Rsvd4'], axis=1, errors='ignore')
    
    # Common Info
    drop_cols = ['TradDt','BizDt','Sgmt','Src','SsnId','FinInstrmId','XpryDt','FinInstrmNm','LastPric']
    common_df = pd.DataFrame([fo.loc[fo.index[1], drop_cols]])
    
    # Determine expiry
    exp = pd.to_datetime(fo['FininstrmActlXpryDt'], errors='coerce')
    today = pd.Timestamp.today().normalize()
    monthly_exp = exp[exp>=today].groupby([exp.dt.year, exp.dt.month]).max().sort_values()
    if monthly_exp.empty: return "<h3>No valid expiry found</h3>"
    expiry = monthly_exp.iloc[0].strftime("%d-%m-%Y")
    common_df.insert(0, 'Expiry', expiry)
    
    # Filter by symbol + expiry
    fo['EXP_DMY'] = pd.to_datetime(fo['FininstrmActlXpryDt']).dt.strftime("%d-%m-%Y")
    df = fo[(fo['TckrSymb']==symbol) & (fo['EXP_DMY']==expiry)].copy()
    df.drop(columns=drop_cols, inplace=True, errors='ignore')

    future_df = df[(df['FinInstrmTp']=='STF') | (df['FinInstrmTp']=='IDF')].copy()
    option_df = df[(df['FinInstrmTp']=='STO') | (df['FinInstrmTp']=='IDO')].copy()
    option_chain_df = build_option_chain(option_df)

    # Build combined HTML
    html = df_to_html(common_df, "Common Info") + "<br><br>"
    html += df_to_html(future_df, "Future Contracts") + "<br><br>"
    html += df_to_html(option_chain_df, "Option Chain")
    return html
'''
# ----------------- Example Usage -----------------
if __name__ == "__main__":
    date_str = "16-12-2025"
    symbol = "NIFTY"
    html_output = nse_fno_html(date_str, symbol)
    # Save to file or render in web page
    with open("fno.html", "w") as f:
        f.write(html_output)
    print("HTML saved to fno.html")
'''